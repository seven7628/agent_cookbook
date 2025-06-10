from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
from typing import Annotated
from langchain_ollama import ChatOllama
from IPython.display import display, Image


llm = ChatOllama(model="qwen2.5:7b", base_url="http://localhost:11434")

class State(TypedDict):
    messages: Annotated[list, add_messages]


graph = StateGraph(State)


def chatbot(state: State):
    print("chatbot", state["messages"])
    return {
        "messages": [llm.invoke(state["messages"])]
    }

graph.add_node("chatbot", chatbot)
graph.add_edge(START, "chatbot")

base = graph.compile(debug=False)

# 通过Image，display展示调用链
# try:
#     display(Image(base.get_graph().draw_mermaid_png()))
# except Exception as e:
#     print("Error: ", e)

# 运行chatbot

def stream_graph_updates(user_input: str):
    for event in base.stream({"messages": [{"role": "user", "content": user_input}]}):
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