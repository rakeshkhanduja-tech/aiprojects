from langchain_google_genai import ChatGoogleGenerativeAI
from agentflow.graph.state import AgentState

def researcher_agent(state: AgentState):
    """
    Researcher Agent: Gathers facts and context based on the plan.
    """
    print("--- RESEARCHER ---")
    plan = state["plan"]
    user_goal = state["user_goal"]
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
    
    # Simulate research by summarizing what needs to be found for the plan.
    # In production, this would use TavilySearch or other tools.
    prompt = f"""You are a Researcher Agent.
The team is working on the following goal: {user_goal}
The plan is: {", ".join(plan)}

Gather detailed context and facts needed to complete this plan. 
Provide a comprehensive summary of findings that the Executor agent can use.
"""
    
    response = llm.invoke(prompt)
    
    return {
        "research_notes": response.content
    }
