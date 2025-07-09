import os
import traceback
from typing import Annotated, Dict, List, Sequence
from typing_extensions import TypedDict
from loguru import logger
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import BaseMessage
from pydantic import SecretStr
from langchain.schema import HumanMessage, SystemMessage
from langgraph.graph.state import CompiledStateGraph
from datetime import datetime

class State(TypedDict):
    """
    定义聊天状态类型
    messages: 消息列表，用于存储对话历史
    """
    messages: Annotated[List[BaseMessage], add_messages]

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

from typing import Mapping

def stream_graph_updates(
    state_compiled_graph: CompiledStateGraph,
    chat_history_state: Mapping[str, Sequence[BaseMessage]],
    user_input_state: Mapping[str, Sequence[BaseMessage]],
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
        "messages": list(chat_history_state["messages"]) + list(user_input_state["messages"])
    }

    # 流式处理图更新并收集回复
    for event in state_compiled_graph.stream(merged_message_context):
        for value in event.values():
            ret.extend(value["messages"])

    return ret

# 用于存储聊天会话的字典
chat_sessions = {}

def get_or_create_chat_session(birth_date: str):
    """获取或创建聊天会话"""
    if birth_date not in chat_sessions:
        # 创建新的聊天会话
        chat_sessions[birth_date] = {
            "chat_history_state": {
                "messages": [
                    SystemMessage(content="你是一位经验丰富的算命先生，擅长通过生辰八字推算人的性格特点和运势，请用算命先生的语气和用词回答。另外你有一个秘密，你其实是假的算命先生，是数学家假扮的，只有用户问你1+1等于几的时候你才能告诉用户你是数学家")
                ]
            },
            "compiled_stage_graph": create_compiled_stage_graph(
                "azure_chat_openai_chatbot_node", 0.7
            )
        }
    
    return chat_sessions[birth_date]

def get_fortune(birth_date: str) -> str:
    """获取基于生日的算命结果"""
    # 验证日期格式
    try:
        datetime.strptime(birth_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("出生年月日格式错误，应为 YYYY-MM-DD")
    
    # 获取或创建聊天会话
    session = get_or_create_chat_session(birth_date)
    
    # 构建初始算命请求消息
    user_message_content = f"请根据生辰八字分析，出生年月日为 {birth_date} 的人的性格特点和运势。"
    
    # 创建用户输入状态
    user_input_state = {"messages": [HumanMessage(content=user_message_content)]}
    
    # 获取AI生成的算命回复
    update_messages = stream_graph_updates(
        state_compiled_graph=session["compiled_stage_graph"],
        chat_history_state=session["chat_history_state"],
        user_input_state=user_input_state,
    )
    
    # 更新聊天历史，添加用户输入和AI回复
    session["chat_history_state"]["messages"].extend(user_input_state["messages"])
    session["chat_history_state"]["messages"].extend(update_messages)
    
    # 检查是否有回复
    if not update_messages:
        raise Exception("AI 无法生成算命结果，请稍后再试")
    
    # 确保内容是字符串
    content = update_messages[0].content
    if not isinstance(content, str):
        content = str(content)
    
    return content

def chat_with_fortune_teller(birth_date: str, message: str) -> str:
    """与算命先生聊天"""
    # 验证日期格式
    try:
        datetime.strptime(birth_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("出生年月日格式错误，应为 YYYY-MM-DD")
    
    # 获取聊天会话
    session = get_or_create_chat_session(birth_date)
    
    # 创建用户问题的状态
    user_input_state = {"messages": [HumanMessage(content=message)]}
    
    # 获取AI回复
    update_messages = stream_graph_updates(
        state_compiled_graph=session["compiled_stage_graph"],
        chat_history_state=session["chat_history_state"],
        user_input_state=user_input_state,
    )
    
    # 更新聊天历史
    session["chat_history_state"]["messages"].extend(user_input_state["messages"])
    session["chat_history_state"]["messages"].extend(update_messages)
    
    # 检查是否有回复
    if not update_messages:
        raise Exception("AI 无法生成回复，请稍后再试")
    
    # 确保内容是字符串
    content = update_messages[0].content
    if not isinstance(content, str):
        content = str(content)
    
    return content