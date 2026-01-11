import json
from langchain_google_genai import ChatGoogleGenerativeAI
from agentflow.graph.state import AgentState

def planner_agent(state: AgentState):
    """
    Planner Agent: Breaks user goal into structured steps.
    """
    print("--- PLANNER ---")
    user_goal = state["user_goal"]
    
    # Using Google Gemini
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
    
    prompt = f"""You are a Strategic Planner Agent.
Your goal is to break down the following high-level objective into 3-5 logical steps for a multi-agent team.
Objective: {user_goal}

Format your response as a JSON list of strings.
Example: ["Step 1", "Step 2", "Step 3"]
"""
    
    response = llm.invoke(prompt)
    try:
        # Simple extraction logic for demo
        content = response.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        plan = json.loads(content)
    except Exception as e:
        print(f"Error parsing plan: {e}")
        plan = [f"Step 1: Explore {user_goal}", "Step 2: Execute", "Step 3: Validate"]

    return {
        "plan": plan,
        "current_step": 0
    }
