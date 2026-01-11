import os
from dotenv import load_dotenv
from agentflow.graph.workflow import define_workflow

load_dotenv()

def run_demo():
    print("=== AGENTFLOW DEMO ===")
    
    # Initialize the graph
    app = define_workflow()
    
    # Define initial state
    initial_state = {
        "user_goal": "Analyze whether we should launch an AI customer support agent for a fintech startup in India. Consider cost, compliance, and ROI.",
        "plan": [],
        "research_notes": "",
        "draft_output": "",
        "validation_feedback": "",
        "retry_count": 0,
        "current_step": 0
    }
    
    # Run the graph
    print(f"Goal: {initial_state['user_goal']}")
    
    for event in app.stream(initial_state):
        for node, values in event.items():
            print(f"\n[NODE]: {node.upper()}")
            # print(f"Values updated: {list(values.keys())}")
            
    print("\n=== FINAL OUTPUT ===")
    # Note: State is preserved in the graph execution result
    # In streaming mode, the final state is the last event.
    
if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set your OPENAI_API_KEY in the .env file.")
    else:
        run_demo()
