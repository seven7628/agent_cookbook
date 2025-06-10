from langchain_community.tools import tool
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from typing_extensions import TypedDict
from typing import Annotated
from langchain_core.messages import ToolMessage
import json

class State(TypedDict):
    messages: Annotated[list, add_messages]


@tool
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

graph_builder = StateGraph(State)

llm = ChatOllama(base_url='http://localhost:11434', model='qwen2.5:7b')
llm_bind_tools = llm.bind_tools([add])

def chatbot(state: State):
    return {
        "messages": [llm_bind_tools.invoke(state["messages"])]
    }

# 添加一个节点
graph_builder.add_node("chatbot", chatbot)


class BasicToolNode:

    def __init__(self, tools: list) -> None:
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, inputs: dict):
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No messages found in inputs")

        outputs = []
        for tool_call in message.tool_calls:
            tool_result = self.tools_by_name[tool_call["name"]].invoke(tool_call["args"])

            outputs.append(
                ToolMessage(
                    tool_call_id=tool_call["id"],
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                )
            )
        return {"messages": outputs}

#tool_node = BasicToolNode([add])
tool_node = ToolNode(tools=[add]) # 使用prebuilt的ToolNode
graph_builder.add_node("tools", tool_node)


def route_tools(state: State):
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError("No messages found in state")
    
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return END

#graph_builder.add_conditional_edges(
#    "chatbot",
#    route_tools,
#    {"tools": "tools", END: END},
#)

graph_builder.add_conditional_edges("chatbot", route_tools)

graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")
graph = graph_builder.compile(debug=True)


def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant: ", value["messages"][-1].content)


if __name__ == '__main__':
    while True:
        try:
            user_input = input("User: ")
            if user_input == "exit":
                break
            stream_graph_updates(user_input)
        except Exception as e:
            print("Error: ", e)
            break