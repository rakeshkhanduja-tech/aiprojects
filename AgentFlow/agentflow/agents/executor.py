from langchain_google_genai import ChatGoogleGenerativeAI
from agentflow.graph.state import AgentState

def executor_agent(state: AgentState):
    """
    Executor Agent: Produces final output based on plan and research.
    """
    print("--- EXECUTOR ---")
    user_goal = state["user_goal"]
    plan = state["plan"]
    research_notes = state["research_notes"]
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)
    
    prompt = f"""You are an Executor Agent.
Objective: {user_goal}
Original Plan: {", ".join(plan)}
Research Findings: {research_notes}

Based on the research and the plan, produce the final high-quality output.
"""
    
    response = llm.invoke(prompt)
    
    return {
        "draft_output": response.content
    }
