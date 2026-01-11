import os
import subprocess
import time
import sys
import yaml
from dotenv import load_dotenv

load_dotenv()

def check_config():
    config_path = "config/config.yaml"
    if not os.path.exists(config_path):
        print("Creating config.yaml from template...")
        with open("config/config.yaml.example", "r") as f:
            template = f.read()
        with open(config_path, "w") as f:
            f.write(template)
        print("IMPORTANT: Please update config/config.yaml with your PostgreSQL credentials.")
        return False
    return True

def run_service(name, command):
    print(f"Starting {name}...")
    return subprocess.Popen(command, shell=True)

def main():
    if not check_config():
        sys.exit(1)

    # Start MCP Server
    mcp_proc = run_service("MCP Producer Server", "python -m mcp_server.server")
    
    # Wait for MCP server to initialize DB and start
    print("Waiting for MCP Server to be ready...")
    time.sleep(5)
    
    # Start Consumer Agent API
    agent_proc = run_service("Sales Consumer Agent API", "python -m sales_agent.api")
    
    # Simple static file server for UI (FastAPI handles it in production, but for demo we can use python -m http.server)
    print("UI is available via the Sales Consumer Agent API (Static files served via FastAPI)")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping services...")
        mcp_proc.terminate()
        agent_proc.terminate()
        print("Done.")

if __name__ == "__main__":
    main()
