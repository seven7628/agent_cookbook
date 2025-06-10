from typing import Annotated
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict
from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import MemorySaver


class State(TypedDict):
    messages: Annotated[list, add_messages]
    name: str
    birthday: str


@tool
def human_assistance(name: str, birthday: str, tool_call_id: Annotated[str, InjectedToolCallId]) -> str:
    """Human assistance to answer questions."""

    human_response = interrupt({
        "question": "是否确认?",
        "name": name,
        "birthday": birthday,
    })

    if human_response.get("correct", "").lower() == "y":
        verify_name = name
        verify_birthday = birthday
        response = "Correct"
    else:
        verify_name = human_response.get("name", name)
        verify_birthday = human_response.get("birthday", birthday)
        response = f"Made a correction: {human_response}"


    state_update = {
        "name": verify_name,
        "birthday": verify_birthday,
        "messages": [ToolMessage(response, tool_call_id=tool_call_id)],
    }
    return Command(update=state_update)

graph_builder = StateGraph(State)
graph_builder.add_node("human_assistance", human_assistance)
tools = [human_assistance]
llm = ChatOllama(model="qwen2.5:7b", base_url="http://localhost:11434")
llm_bind_tools = llm.bind_tools(tools)

def chatbot(state: State):
    message = llm_bind_tools.invoke(state["messages"])
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
graph = graph_builder.compile(checkpointer=memory)

user_input = (
    "John birthday when?"
    "When you have the answer, use the human_assistance tool for review."
)
config = {"configurable": {"thread_id": "1"}}

events = graph.stream(
    {"messages": [{"role": "user", "content": user_input}, {"role": "assistant", "content": "I am John, and my birthday is 1990-01-01."}]},
    config,
    stream_mode="values",
)
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()


# 增加human_command
human_command = Command(
    resume={
        "name": "John",
        "birthday": "1990-01-01",
    },
)

events = graph.stream(human_command, config, stream_mode="values")
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()