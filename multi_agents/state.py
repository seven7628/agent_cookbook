from langgraph.graph import MessagesState
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from typing_extensions import TypedDict


class StepState(BaseModel):
    """
    任务步骤的状态
    """
    
    title: str = Field(description="The title of the section.")
    description: str = Field(description="The content of the section.")
    tool_name: str = Field(description="The name of the tool to use.")
    tool_params: Dict[str, Any] = Field(description="The parameters of the tool.")
    answer: Any = Field(description="The answer of the tool.")
    failed: bool = Field(description="Whether the step failed.")

class PlanState(BaseModel):
    """
    任务计划的状态
    """

    steps: list[StepState] = Field(description="The steps of the plan.")
    current_step: int = Field(description="The current step of the plan.")

class EvalState(BaseModel):
    """
    任务评估的状态
    """
    explain: str = Field(description="The evaluation explain of the plan.")
    result: str = Field(description="The evaluation result of the plan.")
    update_plan: bool | None = Field(description="是否需要对计划进行更新。")
    tool_params: Dict[str, Any] | None = Field(description="The parameters of the tool.")

class State(BaseModel):
    question: str = Field(description="The question of the user.")
    human_feedback: bool | None = Field(description="The human feedback of the plan.")
    plan: PlanState | None = Field(description="The plan of the task.")
    current_state: StepState | None = Field(description="The current state of the task.")
    final_answer: str | None = Field(description="The final answer of the task.")