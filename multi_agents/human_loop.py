from langgraph.types import interrupt, Command
from langchain_core.tools import tool
from state import State
from langchain_ollama import ChatOllama


@tool
def human_assistance(continued: bool) -> str:
    """Get human feedback on the generated message."""
    print("进入到人类返回工具中!!!")
    human_feedback = interrupt({"human_feedback": continued})
    return human_feedback["data"]


def human_loop_node(state: State):
    llm = ChatOllama(
        model="qwen3:latest",
        base_url="http://localhost:11434"
    )

    human_loop = llm.bind_tools([human_assistance])
    human_feedback = human_loop.invoke(
        f"Question: {state.question}\n"
        f"Plans: {state.plan.steps}\n"
        "请调用human_assistance工具，来获取用户的反馈，是否希望任务继续进行。\n"
    )
    print("human_feedback:", human_feedback)
    if len(human_feedback.tool_calls) > 0:
        for tool_call in human_feedback.tool_calls:
            if tool_call['name'] != "human_assistance":
                continue
            human_feedback = tool_call['args']["continued"]
    else:
        human_feedback = False

    if human_feedback:
        return Command(
            goto="tools",
            update={
                "human_feedback": human_feedback,
            }
        )
    return Command(
        goto="end",
        update={
            "human_feedback": human_feedback,
        }
    )