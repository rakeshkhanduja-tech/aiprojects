import os
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from dotenv import load_dotenv
from agentflow.graph.workflow import define_workflow

load_dotenv()

app = FastAPI(title="AgentFlow Multi-Agent System")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global store for demo purposes (In-memory)
execution_logs = []
current_agent_state = {}

class TaskRequest(BaseModel):
    goal: str

@app.get("/")
async def root():
    return {"message": "AgentFlow API is active"}

@app.get("/graph")
async def get_graph():
    """Returns the Mermaid graph for visualization"""
    workflow = define_workflow()
    return {"mermaid": workflow.get_graph().draw_mermaid()}

@app.post("/run")
async def run_task(request: TaskRequest, background_tasks: BackgroundTasks):
    """Triggers the multi-agent flow"""
    global execution_logs, current_agent_state
    execution_logs = []
    
    workflow = define_workflow()
    
    initial_state = {
        "user_goal": request.goal,
        "plan": [],
        "research_notes": "",
        "draft_output": "",
        "validation_feedback": "",
        "retry_count": 0,
        "current_step": 0
    }
    
    def execute_workflow():
        global current_agent_state
        for event in workflow.stream(initial_state):
            for node, values in event.items():
                log_entry = {
                    "node": node,
                    "updates": {k: str(v)[:200] + "..." if isinstance(v, str) and len(str(v)) > 200 else v for k, v in values.items()}
                }
                execution_logs.append(log_entry)
                current_agent_state.update(values)

    background_tasks.add_task(execute_workflow)
    return {"status": "started", "goal": request.goal}

@app.get("/logs")
async def get_logs():
    return {"logs": execution_logs}

@app.get("/state")
async def get_state():
    return current_agent_state

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
