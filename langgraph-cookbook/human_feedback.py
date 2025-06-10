from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import tool
from langgraph.types import Command, interrupt
from pydantic import config
from typing_extensions import TypedDict
from typing import Annotated


@tool
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

class State(TypedDict):
    messages: Annotated[list, add_messages]

@tool
def human_assistance(query: str) -> str:
    """Get human feedback on the generated message."""

    print("进入到人类返回工具中!!!")
    human_feedback = interrupt({"query": query})
    return human_feedback["data"]


tools = [human_assistance, add]
graph_builder = StateGraph(State)
llm = ChatOllama(base_url="http://localhost:11434", model="qwen2.5:7b")
llm_bind_tools = llm.bind_tools(tools)


def chatbot(state: State):
    message = llm_bind_tools.invoke(state["messages"])
    # Because we will be interrupting during tool execution,
    # we disable parallel tool calling to avoid repeating any
    # tool invocations when we resume.
    assert len(message.tool_calls) <= 1
    return {"messages": [message]}

graph_builder.add_node("chatbot", chatbot)
tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)

graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")

memory = MemorySaver()
graph = graph_builder.compile(debug=True, checkpointer=memory)

# 测试human_feedback, 如果想测试可以打开以下注释代码
# user_input = "我在构建一个人工智能代理方面需要一些专家指导。你能帮我请求协助吗？比如使用human_assistance工具来获取用户的反馈。"
user_input = "在回答这个问题之前，你可以调用human_assistance工具来获取用户的反馈。并且接收到回复后用户add工具来计算结果。接下来开始回答吧! 问题: 56 + 66 + 76 =? "
# system_message = """你是一个专业的数据智能体，能够帮助用户解决数据计算问题。在回答用户前需要调用human_assistance工具等待用户回复: <YES>。 
# 请确保用户在回复<YES>之后再继续帮助用户解答问题。接下来请帮助用户解决问题吧！"""

config = {"configurable": {"thread_id": "1"}}
events = graph.stream({"messages": [{"role": "user", "content": user_input}]}, config, stream_mode="values")
# events = graph.stream({"messages": [{"role": "system", "content":system_message},{"role": "user", "content": user_input}]}, config, stream_mode="values")

print("@@@@@@@@@@@@@@@@@@@@@@@@@")
for event in events:
    if "messages" in event:
        print(event["messages"][-1].pretty_print())
print("@@@@@@@@@@@@@@@@@@@@@@@@@")


# 恢复运行, 利用Command来恢复运行
# human_response = (
#     "用户回复了<YES>, 请继续帮助用户解答问题。\n"
# )
# human_command = Command(resume={"data": human_response})
# events = graph.stream(human_command, config, stream_mode="values")

# print("##############################")
# for event in events:
#     if "messages" in event:
#         event["messages"][-1].pretty_print()
# print("##############################")