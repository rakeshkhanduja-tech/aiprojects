import os
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from agentflow.main import app

load_dotenv()

# Mount static files to serve the UI
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    # Check for keys
    if not os.getenv("GOOGLE_API_KEY") or "your_key_here" in os.getenv("GOOGLE_API_KEY"):
        print("\n" + "!"*50)
        print("CRITICAL ERROR: GOOGLE_API_KEY is missing or invalid.")
        print("Please update the .env file with your real Google API key.")
        print("!"*50 + "\n")
    else:
        # Start the server (includes the UI)
        uvicorn.run(app, host="0.0.0.0", port=8000)
