from state import State

def cond_to_tools_or_human_loop(state: State):
    """如果用户已经确定计划没有问题, 则直接进入tools agent节点"""
    if state.plan is None or len(state.plan.steps) == 0:
        return "end"
    if state.human_feedback:
        return "tools"
    return "human_loop"

# def cond_to_tools_or_end(state: State):
#     if state.human_feedback:
#         return "tools"
#     return "human_loop"

def cond_to_tools_or_end(state: State):
    print("进入cond_to_tools_or_end条件判断")
    if len(state.plan.steps) > 0:
        all_complete = True
        for plan in state.plan.steps:
            if not plan.answer:
                all_complete = False
                break
        if all_complete:
            return "tools"
        else:
            return "end"
    return "end"