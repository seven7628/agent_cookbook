from langgraph.types import Command
from state import PlanState, State
from tools import tool_list
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage


def create_planner():
    llm = ChatOllama(
        model="qwen2.5:7b",
        base_url="http://localhost:11434",
        verbose=True,
    )
    planner = llm.with_structured_output(PlanState)
    # planner = create_react_agent(llm, tools, prompt=planner_prompt.format(tools=tools), debug=True)
    return planner

def planner_node(state: State):
    question = state.question
    planner = create_planner()

    planner_prompt = """你是一个专业的任务规划助手。能够根据任务描述，选择合适的工具，并生成相应的任务计划。
    可用工具: {tools}。
    输出结构：期望已Json结构化数据进行输出。下面是结构化数据的详细定义与描述：
    {plan}
    接下来请帮助用户生成任务计划吧。
    """
    tools = [
        {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.args_schema.model_json_schema()["properties"],
        }
    
        for tool in tool_list
    ]

    plan = planner.invoke([
        SystemMessage(content=planner_prompt.format(tools=tools, plan=PlanState.model_json_schema())),
        HumanMessage(content=question)]
        )
    print("planner节点的输出", plan)
    if plan is None:
        return Command(
            goto="end",
            update={
                "plan": None,
                "current_state": None,
                "final_answer": "抱歉，我无法理解您的问题。请您重新描述您的问题。（计划生成失败!!）"
            },
        )
    return Command(
        update={
        "plan": plan,
        "current_state": plan.steps[0]
    })

if __name__ == "__main__":
    state = State(
        question="请计算1+2+3+4+5",
        human_feedback=None,
        plan=None,
        current_state=None,
        final_answer=None
    )
    
    print(planner_node(state))