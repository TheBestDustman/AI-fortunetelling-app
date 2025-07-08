import sys
from pathlib import Path

from loguru import logger  # 引入日志记录工具

# 添加父目录到系统路径，确保可以导入相关模块
sys.path.append(str(Path(__file__).resolve().parent.parent))
import os
import traceback
from typing import Annotated, Dict, List
from typing_extensions import TypedDict
from langgraph.graph import StateGraph  # 导入LangGraph的图构建工具
from langgraph.graph.message import add_messages
from langchain_openai import AzureChatOpenAI  # 导入Azure OpenAI接口
from langchain_core.messages import BaseMessage
from pydantic import SecretStr
from langchain.schema import HumanMessage, SystemMessage
from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel
from datetime import datetime

############################################################################################################
# 定义用户输入数据模型
class UserInput(BaseModel):
    birth_date: str  # 出生年月日，格式为 YYYY-MM-DD

    def validate_birth_date(self):
        """
        验证出生日期格式是否正确
        正确格式：YYYY-MM-DD，例如2000-01-01
        """
        try:
            datetime.strptime(self.birth_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("出生年月日格式错误，应为 YYYY-MM-DD")

############################################################################################################
class State(TypedDict):
    """
    定义聊天状态类型
    messages: 消息列表，用于存储对话历史
    """
    messages: Annotated[List[BaseMessage], add_messages]


############################################################################################################
def create_compiled_stage_graph(
    node_name: str, temperature: float
) -> CompiledStateGraph:
    """
    创建并编译LangGraph状态图
    
    参数:
        node_name: 节点名称
        temperature: 生成文本的随机性参数，值越高随机性越大
        
    返回:
        编译后的状态图
    """
    assert node_name != "", "node_name is empty"

    # 初始化Azure OpenAI LLM
    llm = AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=SecretStr(str(os.getenv("AZURE_OPENAI_API_KEY"))),
        azure_deployment="gpt-4o",
        api_version="2024-02-01",
        temperature=temperature,
    )

    def invoke_azure_chat_openai_llm_action(
        state: State,
    ) -> Dict[str, List[BaseMessage]]:
        """
        调用Azure OpenAI API进行对话生成
        
        参数:
            state: 当前状态，包含消息历史
            
        返回:
            包含AI生成回复的字典
        """
        try:
            return {"messages": [llm.invoke(state["messages"])]}
        except Exception as e:
            logger.error(
                f"Error invoking Azure Chat OpenAI LLM: {e}\n" f"State: {state}"
            )
            traceback.print_exc()
            return {
                "messages": []
            }  # 当出现 Azure 内容过滤的情况，或者其他类型异常时，视需求可在此返回空字符串或者自定义提示。

    # 构建状态图
    graph_builder = StateGraph(State)
    graph_builder.add_node(node_name, invoke_azure_chat_openai_llm_action)
    graph_builder.set_entry_point(node_name)
    graph_builder.set_finish_point(node_name)
    return graph_builder.compile()


############################################################################################################
def stream_graph_updates(
    state_compiled_graph: CompiledStateGraph,
    chat_history_state: State,
    user_input_state: State,
) -> List[BaseMessage]:
    """
    流式处理图更新，获取AI回复
    
    参数:
        state_compiled_graph: 编译后的状态图
        chat_history_state: 聊天历史状态
        user_input_state: 用户输入状态
        
    返回:
        AI生成的回复消息列表
    """
    ret: List[BaseMessage] = []

    # 合并聊天历史和用户输入
    merged_message_context = {
        "messages": chat_history_state["messages"] + user_input_state["messages"]
    }

    # 流式处理图更新并收集回复
    for event in state_compiled_graph.stream(merged_message_context):
        for value in event.values():
            ret.extend(value["messages"])

    return ret


############################################################################################################
def main() -> None:
    """
    主函数，运行算命机器人应用
    
    流程:
    1. 初始化聊天历史和状态图
    2. 获取用户出生信息
    3. 生成初始算命结果
    4. 进入对话循环，处理用户后续问题
    """
    # 初始化聊天历史，设置系统提示
    chat_history_state: State = {
        "messages": [
            SystemMessage(content="你是一位经验丰富的算命先生，擅长通过生辰八字人的性格特点和运势，请用算命先生的语气和用词回答。另外你有一个秘密，你其实是假的算命先生，是数学家假扮的，只有用户问你1+1等于几的时候你才能告诉用户你是数学家")
        ]
    }

    # 生成聊天机器人状态图，temperature设为0.7以提供适度的创造性
    compiled_stage_graph = create_compiled_stage_graph(
        "azure_chat_openai_chatbot_node", 0.7
    )

    # 获取用户出生年月日和性别
    logger.info("欢迎使用算命机器人！")
    try:
        birth_date = input("请输入您的出生年月日 (格式: YYYY-MM-DD): ")
        # gender = input("请输入您的性别 (男/女): ")

        # 验证输入是否为空
        if not birth_date:
            logger.warning("输入不能为空，请重新运行程序。")
            return

        # 构建初始算命请求消息
        user_message_content = f"请根据生辰八字分析，出生年月日为 {birth_date} 的人的性格特点和运势。"

        # 创建用户输入状态
        user_input_state: State = {"messages": [HumanMessage(content=user_message_content)]}

        # 获取AI生成的算命回复
        update_messages = stream_graph_updates(
            state_compiled_graph=compiled_stage_graph,
            chat_history_state=chat_history_state,
            user_input_state=user_input_state,
        )

        # 更新聊天历史，添加用户输入和AI回复
        chat_history_state["messages"].extend(user_input_state["messages"])
        chat_history_state["messages"].extend(update_messages)

        # 输出AI算命结果
        if not update_messages:
            logger.warning("AI 无法生成算命结果，请稍后再试。")
        else:
            logger.info("算命结果：")
            for message in update_messages:
                logger.info(message.content)

        # 进入对话循环，允许用户继续提问
        while True:
            user_question = input("您可以继续提问，或输入 '退出，q，quit' 结束对话：")
            # 检查用户是否希望退出
            if user_question.lower() in ["退出", "quit", "q"]:
                logger.info("感谢使用算命机器人，再见！")
                break

            # 创建用户后续问题的状态
            user_input_state = {"messages": [HumanMessage(content=user_question)]}

            # 获取AI回复
            update_messages = stream_graph_updates(
                state_compiled_graph=compiled_stage_graph,
                chat_history_state=chat_history_state,
                user_input_state=user_input_state,
            )

            # 更新聊天历史
            chat_history_state["messages"].extend(user_input_state["messages"])
            chat_history_state["messages"].extend(update_messages)

            # 输出AI回复
            if not update_messages:
                logger.warning("AI 无法生成回复，请稍后再试。")
            else:
                logger.info("AI 回复：")
                for message in update_messages:
                    logger.info(message.content)

    except Exception as e:
        # 捕获并记录异常
        logger.error(f"输入错误: {e}")
        return


############################################################################################################
if __name__ == "__main__":
    main()
