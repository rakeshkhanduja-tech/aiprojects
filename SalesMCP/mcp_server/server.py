import os
import yaml
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from mcp_server.tools import MCPTools
from database.manager import DatabaseManager

app = FastAPI(title="SalesMCP Producer Server")

# Initialize DB and Tools
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "config.yaml")
if not os.path.exists(CONFIG_PATH):
    # Fallback for demo/dev
    CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "config.yaml.example")

db = DatabaseManager(CONFIG_PATH)
mcp_tools = MCPTools(db)

# Automated DB Setup on startup
@app.on_event("startup")
async def startup_event():
    print("[DEBUG] MCP Server starting up...")
    schema_path = os.path.join(os.path.dirname(__file__), "..", "database", "schema.sql")
    seed_path = os.path.join(os.path.dirname(__file__), "..", "database", "seed.py")
    try:
        db.setup_database(schema_path)
        # Check if seeded
        res = db.query("SELECT COUNT(*) FROM users")
        if res[0]['count'] == 0:
            print("[DEBUG] Database empty. Running seed scripts...")
            db.seed_data(seed_path)
        print("[DEBUG] Database initialization complete.")
    except Exception as e:
        print(f"[CRITICAL] Startup Database Error: {e}")

class DecisionLog(BaseModel):
    agent_name: str
    input_question: str
    recommendation: str
    confidence: float
    evidence: Dict[str, Any]

@app.get("/capabilities")
async def get_capabilities():
    print("[DEBUG] Client requested capabilities list.")
    return {
        "capabilities": [
            "get_sales_pipeline_summary",
            "get_deals_by_owner",
            "get_customer_profile",
            "get_stalled_deals",
            "evaluate_deal_risk",
            "prioritize_deals_for_today",
            "check_sales_policy",
            "log_agent_decision"
        ]
    }

@app.get("/tools/{tool_name}")
async def call_tool(tool_name: str, param: Optional[str] = None, id: Optional[int] = None):
    print(f"[DEBUG] MCP Tool Call: {tool_name} | Params: param={param}, id={id}")
    try:
        if tool_name == "get_sales_pipeline_summary":
            return mcp_tools.get_sales_pipeline_summary()
        elif tool_name == "get_deals_by_owner":
            return mcp_tools.get_deals_by_owner(param)
        elif tool_name == "get_customer_profile":
            return mcp_tools.get_customer_profile(id)
        elif tool_name == "get_stalled_deals":
            return mcp_tools.get_stalled_deals()
        elif tool_name == "evaluate_deal_risk":
            return mcp_tools.evaluate_deal_risk(id)
        elif tool_name == "prioritize_deals_for_today":
            # Fallback if id is missing
            target_id = id
            if not target_id:
                print("[DEBUG] No owner_id provided for prioritization. Attempting name lookup...")
                if param:
                    # Look up by name if possible?
                    pass
            return mcp_tools.prioritize_deals_for_today(target_id)
        elif tool_name == "check_sales_policy":
            return mcp_tools.check_sales_policy(param)
        else:
            print(f"[DEBUG] Tool not found: {tool_name}")
            raise HTTPException(status_code=404, detail="Tool not found")
    except Exception as e:
        print(f"[ERROR] MCP Tool Exception: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/log")
async def log_decision(decision: DecisionLog):
    print(f"[DEBUG] Logging decision for agent: {decision.agent_name}")
    try:
        return mcp_tools.log_agent_decision(decision.model_dump())
    except Exception as e:
        print(f"[ERROR] Log Decision Failure: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    with open(CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)['mcp']
    uvicorn.run(app, host=config['host'], port=config['port'])
