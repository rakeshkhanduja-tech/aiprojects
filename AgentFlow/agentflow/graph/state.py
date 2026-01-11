from typing import TypedDict, List, Annotated, Optional
import operator

class AgentState(TypedDict):
    """
    Shared memory for the AgentFlow multi-agent system.
    """
    user_goal: str
    plan: List[str]
    research_notes: str
    draft_output: str
    validation_feedback: str
    retry_count: int
    current_step: int
    # history: Annotated[List[dict], operator.add] # Optional: for tracking full trace
