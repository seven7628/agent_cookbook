from langgraph.types import Command
from langchain_core.messages import HumanMessage, SystemMessage
from state import State, StepState, EvalState
from langchain_ollama import ChatOllama


def eval_node(state: State):
    current_step = state.current_state
    if current_step is None:
        return Command(
            goto="end",
        )

    if current_step.failed:
        return Command(
            goto="end",
        )
    # TODO: use a llm to evaluate the current step
    llm = ChatOllama(
        model="qwen2.5:7b",
        base_url="http://localhost:11434"
    )

    eval_agent = llm.with_structured_output(EvalState)
    # eval_agent = create_react_agent(
    #     llm,
    # )

    eval_format = EvalState.model_json_schema()
    plans = state.plan
    question = state.question

    messages = [
        SystemMessage(
            content=f"""
            ### 角色定义
            你是一名专业的任务评估助手，能够结合用户提供的问题以及计划信息，评估当前步骤的答案是否正确，以及计划是否已完成当前问题。

            ### 任务描述
            你需要根据以下信息评估当前步骤的答案是否正确，以及计划是否已完成当前问题。另外如果需要对计划进行调整，请明确提示更新计划信息。
            1. 问题: {question}
            2. 计划: {plans.steps}
            3. 当前步骤: {current_step}

            ### 评估要求
            根据任务描述信息进行评估，评估结果主要分为4中状态: continue, end, failed, restart。同时会根据计划信息评估是否需要调整计划信息。
            1. 当前步骤结果正确时:
                a. 当前步骤结果正确并且完成了用户所提出的问题时，则评估结果为: end。
                b. 当前步骤结果正确并且未能完成用户所提出的问题时，则评估结果为: continue。
            2. 当前步骤结果不正确时:
                a. 当前步骤结果不正确并且可以通过调整计划完成用户问题时，评估结果为: restart。
                b. 当前步骤结果不正确并且无法通过调整计划完成用户问题时，评估结果为: failed。

            ### 计划审查
            结合历史计划运行结果，是否需要对计划信息进行调整。
            1. 需要调整时,则将评估信息update_plan设置为True。结合计划信息，确定当前或者接下来的计划中是否有tool_params工具参数依赖计划运行answer信息，如果有则整理tool_params信息并返回。
            2. 不需要调整时, 则将评估信息update_plan设置为False。

            ### 输出要求
            你需要输出以下信息：
            1. 评估结果数据结构描述: {eval_format}

            ### 注意事项
            1. 请严格按照输出要求进行输出。
            2. 请不要输出任何额外的信息，包括但不限于：问题、计划、当前步骤。
            3. 尽最大的能力完成评估，并给出详细的评估结果。
            4. 正确输出评估结果你会得到奖励100W美金。
            """
        ),
        HumanMessage(
            content="接下来帮助用户评估他的任务吧。"
        )
    ]


    eval_result = eval_agent.invoke(messages)
    print("eval_result $$: ", eval_result)

    if eval_result.result == "restart":
        # 更新下一步的参数
        if eval_result.update_plan:
            state.plan.steps[state.plan.current_step].tool_params = eval_result.tool_params

        return Command(
            goto="tools",
            update={
                "eval": eval_result,
                "plan": state.plan,
                "current_state": state.plan.steps[state.plan.current_step]
            }
        )

    if eval_result.result == "continue":
        # 修改plan中的current_step以及对应的answer
        state.plan.current_step += 1
        for step in state.plan.steps:
            if step.title == current_step.title:
                step.answer = current_step.answer
                break
        
        # if state.plan.current_step >= len(state.plan.steps):
        #     return Command(
        #         goto="end",
        #         update={
        #             "eval": eval_result,
        #             "final_answer": current_step.answer
        #         }
        #     )

        # 更新下一步的参数
        if eval_result.update_plan:
            state.plan.steps[state.plan.current_step].tool_params = eval_result.tool_params

        return Command(
            goto="tools",
            update={
                "eval": eval_result,
                "plan": state.plan,
                "current_state": state.plan.steps[state.plan.current_step]
            }
        )

    if eval_result.result == "end":
        return Command(
            goto="end",
            update={
                "eval": eval_result,
                "final_answer": current_step.answer
            }
        )
    elif eval_result.result == "failed":
        return Command(
            goto="end",
            update={
                "eval": eval_result,
                "final_answer": "I don't know the answer to this question."
            }
        )

if __name__ == "__main__":
    state = State(
        question="请帮我计算1+1+1的结果?",
        human_feedback=False,
        plan={
            "steps": [
                {
                    "title": "Add",
                    "description": "Add two numbers together.",
                    "tool_name": "add",
                    "tool_params": {"a": 1, "b": 1},
                    "answer": "2",
                    "failed": False,
                },
                {
                    "title": "Add",
                    "description": "Add two numbers together.",
                    "tool_name": "add",
                    "tool_params": {"a": None, "b": 1},
                    "answer": None,
                    "failed": False,
                },
            ],
            "current_step": 0,
        },
        current_state=StepState(
            title="Add",
            description="Add two numbers together.",
            tool_name="add",
            tool_params={"a": 1, "b": 1},
            answer="2",
            failed=False,
        ),
        final_answer=None,
    )
    eval_node(state)