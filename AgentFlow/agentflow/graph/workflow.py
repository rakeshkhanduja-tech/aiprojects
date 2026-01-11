from langgraph.graph import StateGraph, END
from agentflow.graph.state import AgentState
from agentflow.agents.planner import planner_agent
from agentflow.agents.researcher import researcher_agent
from agentflow.agents.executor import executor_agent
from agentflow.agents.validator import validator_agent

def define_workflow():
    """
    Defines the multi-agent state machine workflow using LangGraph.
    """
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("planner", planner_agent)
    workflow.add_node("researcher", researcher_agent)
    workflow.add_node("executor", executor_agent)
    workflow.add_node("validator", validator_agent)

    # Set Entry Point
    workflow.set_entry_point("planner")

    # Define Edges
    workflow.add_edge("planner", "researcher")
    workflow.add_edge("researcher", "executor")
    workflow.add_edge("executor", "validator")

    # Define Conditional Edges (Validator -> ???)
    def should_continue(state: AgentState):
        feedback = state.get("validation_feedback", "")
        retry_count = state.get("retry_count", 0)
        
        if "APPROVED" in feedback:
            return "end"
        elif retry_count >= 3:
            print(f"Max retries reached ({retry_count}). Stopping.")
            return "end"
        else:
            # If feedback contains specific instructions, we could route 
            # back to Planner or Executor. Here we'll route back to Planner 
            # to adjust the strategy if needed.
            return "retry"

    workflow.add_conditional_edges(
        "validator",
        should_continue,
        {
            "end": END,
            "retry": "planner"
        }
    )

    return workflow.compile()

# Example usage/export
# app = define_workflow()
