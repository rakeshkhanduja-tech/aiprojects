from langchain_google_genai import ChatGoogleGenerativeAI
from agentflow.graph.state import AgentState

def validator_agent(state: AgentState):
    """
    Validator Agent: Reviews the output and provides feedback or approval.
    """
    print("--- VALIDATOR ---")
    user_goal = state["user_goal"]
    draft_output = state["draft_output"]
    retry_count = state.get("retry_count", 0)
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
    
    prompt = f"""You are a Validator Agent.
Objective: {user_goal}
Draft Output to Review: {draft_output}

Review the output for completeness, accuracy, and quality.
If the output is excellent and meets the goal, start your response with 'APPROVED'.
If it needs improvements, provide specific feedback starting with 'FEEDBACK:'.
Max retries allowed is 3. Current retry count: {retry_count}
"""
    
    response = llm.invoke(prompt)
    feedback = response.content
    
    # Logic for conditional transitions will happen in the graph, 
    # but we store the feedback here.
    return {
        "validation_feedback": feedback,
        "retry_count": retry_count + 1 if "FEEDBACK" in feedback else retry_count
    }
