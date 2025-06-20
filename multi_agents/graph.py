from langgraph.graph import StateGraph, START, END
from eval import eval_node
from tools import tools_node
from human_loop import human_loop_node
from planner import planner_node
from state import State
from cond import cond_to_tools_or_human_loop, cond_to_tools_or_end
from langgraph.checkpoint.memory import InMemorySaver
from IPython.display import display, Image


# builder.add_conditional_edges("eval", cond_to_tools_or_end, {
#     "tools": "tools",
#     "end": END
# })
# builder.add_edge("eval", END)



def create_graph():
    builder = StateGraph(State)
    builder.add_node("planner", planner_node)
    builder.add_node("eval", eval_node)
    builder.add_node("tools", tools_node)
    builder.add_node("human_loop", human_loop_node)

    builder.add_edge(START, "planner")
    builder.add_conditional_edges("planner", cond_to_tools_or_human_loop, {
        "tools": "tools",
        "human_loop": "human_loop",
        "end": END
    })
    builder.add_edge("human_loop", "tools")

    builder.add_edge("tools", "eval")
    checkpointer = InMemorySaver()
    graph = builder.compile(debug=True, checkpointer=checkpointer)
    return graph.with_config({"configurable": {"thread_id": "default"}, "recursion_limit": 20})

if __name__ == "__main__":

    config = {"configurable": {"thread_id": "default"}, "recursion_limit": 20}
    graph = create_graph()
    res = graph.invoke({
        "question": "帮我计算一下(38 * 42) / (12 - 2) 的结果", "human_feedback": True, 
        "plan": None, "current_state": None, "final_answer": None},
    config=config)
    print(res)
    # display(Image(graph.get_graph().draw_mermaid_png()))
    # with open("graph.png", "wb") as f:
        # f.write(graph.get_graph().draw_mermaid_png())
