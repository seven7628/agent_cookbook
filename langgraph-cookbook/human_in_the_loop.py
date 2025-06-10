from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver
from typing import Callable
from langchain_core.tools import BaseTool, tool as create_tool
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt.interrupt import HumanInterrupt, HumanInterruptConfig


def book_hotel(hotel_name:str):
    """Book a hotel."""
    response = interrupt(  
        f"尝试调用通过如下参数信息 {{'hotel_name': {hotel_name}}} 去调用 `book_hotel` 工具。"
        "请确认是否需要修改参数信息。"
    )
    if response["type"] == "accept":
        pass
    elif response["type"] == "edit":
        hotel_name = response["args"]["hotel_name"]
    else:
        raise ValueError(f"Unknown response type: {response['type']}")
    return f"您已成功预定{hotel_name}, 祝您旅途愉快."

def add_human_in_the_loop(
    tool: Callable | BaseTool,
    *,
    interrupt_config: HumanInterruptConfig = None,
) -> BaseTool:
    """Wrap a tool to support human-in-the-loop review.""" 
    if not isinstance(tool, BaseTool):
        tool = create_tool(tool)

    if interrupt_config is None:
        interrupt_config = {
            "allow_accept": True,
            "allow_edit": True,
            "allow_respond": True,
        }

    @create_tool(  
        tool.name,
        description=tool.description,
        args_schema=tool.args_schema
    )
    def call_tool_with_interrupt(config: RunnableConfig, **tool_input):
        request: HumanInterrupt = {
            "action_request": {
                "action": tool.name,
                "args": tool_input
            },
            "config": interrupt_config,
            "description": "Please review the tool call"
        }
        response = interrupt([request])[0]  
        # approve the tool call
        if response["type"] == "accept":
            tool_response = tool.invoke(tool_input, config)
        # update tool call args
        elif response["type"] == "edit":
            tool_input = response["args"]["args"]
            tool_response = tool.invoke(tool_input, config)
        # respond to the LLM with user feedback
        elif response["type"] == "response":
            user_feedback = response["args"]
            tool_response = user_feedback
        else:
            raise ValueError(f"Unsupported interrupt response type: {response['type']}")

        return tool_response

    return call_tool_with_interrupt


llm = ChatOllama(model="qwen2.5:7b", base_url="http://localhost:11434")

checkpinter = InMemorySaver()
agent = create_react_agent(
    llm,
    tools=[add_human_in_the_loop(book_hotel)],
    checkpointer=checkpinter,
    debug=True
)

config = {
   "configurable": {
      "thread_id": "default"
   }
}

for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "预订麦基特里克酒店住宿"}]},
    # Command(resume=[{"type": "accept"}]),
    # Command(resume=[{"type": "edit", "args": {"args": {"hotel_name": "万达酒店"}}}]),
    config=config,
    stream_mode="values"
):
    print(chunk)
    # print("==== \n")
    # print(chunk["messages"][-1].pretty_print())
    print("\n")

