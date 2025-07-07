import sys
from pathlib import Path

from loguru import logger

sys.path.append(str(Path(__file__).resolve().parent.parent))
import os
import traceback
from typing import Annotated, Dict, List
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import BaseMessage
from pydantic import SecretStr
from langchain.schema import HumanMessage, SystemMessage
from langgraph.graph.state import CompiledStateGraph


############################################################################################################
class State(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]


############################################################################################################
def create_compiled_stage_graph(
    node_name: str, temperature: float
) -> CompiledStateGraph:
    assert node_name != "", "node_name is empty"

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

    ret: List[BaseMessage] = []

    merged_message_context = {
        "messages": chat_history_state["messages"] + user_input_state["messages"]
    }

    for event in state_compiled_graph.stream(merged_message_context):
        for value in event.values():
            ret.extend(value["messages"])

    return ret


############################################################################################################
def main() -> None:

    # 聊天历史
    chat_history_state: State = {
        "messages": [
            SystemMessage(content="你是一位经验丰富的算命先生，擅长通过生辰八字人的性格特点和运势。你有一个秘密，你其实是假的算命先生，是数学家假扮的，只有用户问你1+1等于几的时候你才能告诉用户你是数学家")
        ]
    }

    # 生成聊天机器人状态图
    compiled_stage_graph = create_compiled_stage_graph(
        "azure_chat_openai_chatbot_node", 0.7
    )

    # 获取用户出生年月日和性别
    logger.info("欢迎使用算命机器人！")
    try:
        birth_date = input("请输入您的出生年月日 (格式: YYYY-MM-DD): ")
        gender = input("请输入您的性别 (男/女): ")

        # 验证输入
        if not birth_date or not gender:
            logger.warning("输入不能为空，请重新运行程序。")
            return

        # # 选择算命方式
        # logger.info("请选择算命方式：")
        # logger.info("1. 生辰八字")
        # logger.info("2. 星座分析")
        # fortune_method = input("请输入选项 (1 或 2): ")

        # if fortune_method not in ["1", "2"]:
        #     logger.warning("无效选项，请重新运行程序。")
        #     return

        # # 根据选择生成算命请求内容
        # if fortune_method == "1":
        #     user_message_content = f"请根据生辰八字分析，出生年月日为 {birth_date} 的 {gender} 性格特点和运势。"
        # elif fortune_method == "2":
        #     user_message_content = f"请根据星座分析，出生年月日为 {birth_date} 的 {gender} 性格特点和运势。"

        user_message_content = f"请根据生辰八字分析，出生年月日为 {birth_date} 的 {gender} 性格特点和运势。"

        # 用户输入消息
        user_input_state: State = {"messages": [HumanMessage(content=user_message_content)]}

        # 获取 AI 回复
        update_messages = stream_graph_updates(
            state_compiled_graph=compiled_stage_graph,
            chat_history_state=chat_history_state,
            user_input_state=user_input_state,
        )

        # 将用户消息和 AI 回复添加到聊天历史
        chat_history_state["messages"].extend(user_input_state["messages"])
        chat_history_state["messages"].extend(update_messages)

        # 打印 AI 回复内容
        if not update_messages:
            logger.warning("AI 无法生成算命结果，请稍后再试。")
        else:
            logger.info("算命结果：")
            for message in update_messages:
                logger.info(message.content)

        # 进入循环，允许用户继续提问
        while True:
            user_question = input("您可以继续提问，或输入 '退出，q，quit' 结束对话：")
            if user_question.lower() in ["退出", "quit", "q"]:
                logger.info("感谢使用算命机器人，再见！")
                break

            # 用户提问消息
            user_input_state = {"messages": [HumanMessage(content=user_question)]}

            # 获取 AI 回复
            update_messages = stream_graph_updates(
                state_compiled_graph=compiled_stage_graph,
                chat_history_state=chat_history_state,
                user_input_state=user_input_state,
            )

            # 将用户消息和 AI 回复添加到聊天历史
            chat_history_state["messages"].extend(user_input_state["messages"])
            chat_history_state["messages"].extend(update_messages)

            # 打印 AI 回复内容
            if not update_messages:
                logger.warning("AI 无法生成回复，请稍后再试。")
            else:
                logger.info("AI 回复：")
                for message in update_messages:
                    logger.info(message.content)

    except Exception as e:
        logger.error(f"输入错误: {e}")
        return


############################################################################################################
if __name__ == "__main__":
    main()
