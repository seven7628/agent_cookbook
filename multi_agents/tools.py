from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langgraph.types import Command

from state import StepState, State

@tool
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers together."""
    return a * b

@tool
def divide(a: int, b: int) -> int:
    """Divide two numbers together."""
    return a / b

@tool
def subtract(a: int, b: int) -> int:
    """Subtract two numbers together."""
    return a - b


tool_list = [add, multiply, divide, subtract]

def tools_node(state: State):
    current_step = state.current_state
    if current_step is None:
        return Command(
            goto="eval",
        )

    llm = ChatOllama(
        model="qwen2.5:7b", base_url="http://localhost:11434"
    )
    llm = llm.bind_tools(tool_list)
    tool_agent = create_react_agent(llm, tools=tool_list)
    tool_name = current_step.tool_name
    tool_params = current_step.tool_params
    try:
        res = tool_agent.invoke({"messages": [f"Use {tool_name} to calculate {tool_params}"]})
        print("tool message ##: ", res['messages'][-2].content)
        current_step.answer = res['messages'][-2].content
        
    except Exception as e:
        print(e)
        current_step.failed = True
    
    return Command(
        goto="eval",
        update={
            "current_state": current_step,
        }
    )


if __name__ == "__main__":
    state = State(
        question="What is 1 + 1?",
        human_feedback=False,
        plan={
            "steps": [
                {
                    "title": "Add",
                    "description": "Add two numbers together.",
                    "tool_name": "add",
                    "tool_params": {"a": 1, "b": 1},
                    "answer": None,
                    "failed": False,
                }
            ],
            "current_step": 0,
        },
        current_state=StepState(
            title="Add",
            description="Add two numbers together.",
            tool_name="add",
            tool_params={"a": 1, "b": 1},
            answer=None,
            failed=False,
        ),
        final_answer=None,
    )

    resp = tools_node(state)