# SalesMCP: Production MCP Sales Assistant

SalesMCP is a demonstration of the **Model Context Protocol (MCP)** applied to a real-world B2B sales operations use case. It showcases how AI agents can safely and effectively interact with sensitive enterprise data in a PostgreSQL database without direct access.

## Architecture

```
User (Sales Rep) <-> Web UI <-> Sales Consumer Agent (Gemini 2.0)
                                      |
                                      | (MCP Protocol / Tools)
                                      v
                              MCP Producer Agent (Backend) <-> PostgreSQL
```

### Key Components

1.  **MCP Producer Agent (Backend)**: Sits directly in front of PostgreSQL. It exposes **Capabilities** (Tools) rather than tables. It enforces read-only access for queries and maintains a secure write-path for logging decisions.
2.  **Sales Consumer Agent (AI)**: A high-level reasoning agent that understands sales strategy. It never sees a SQL query; it only knows how to ask the MCP server for specific capabilities like `get_stalled_deals` or `evaluate_deal_risk`.
3.  **Shared Business Memory**: All agent decisions are logged back into the `agent_decisions` table via MCP, creating a permanent, auditable record of AI reasoning.

## How to Run

### 1. Prerequisites
- Python 3.9+
- PostgreSQL instance running
- Google API Key (for Gemini 2.0)

### 2. Setup
```bash
cd SalesMCP
pip install -r requirements.txt
cp .env.example .env # Add your GOOGLE_API_KEY
```

### 3. Configuration
Edit `config/config.yaml` with your PostgreSQL credentials.

### 4. Launch
```bash
python main.py
```
This will:
- Automatically create the schema in your PostgreSQL DB.
- Seed it with realistic sales data.
- Start the MCP Producer Server (Port 8001).
- Start the Sales Consumer Agent API (Port 8000).

### 5. Access
Open your browser to `http://localhost:8000/static/index.html` (Note: Ensure your API serves static files or use a simple server).

## Why MCP?

- **Safety**: The AI Agent cannot "hallucinate" SQL that deletes your database. It can only call predefined, safe capabilities.
- **Auditability**: Every decision is stored with the exact "Evidence" (MCP data) used to make it.
- **Decoupling**: You can swap your database or your AI model independently without breaking the contract between the Producer and Consumer.
- **Capability-Based**: MCP focus on *what* the business can do (e.g., "Assess Risk") rather than *where* data is stored.

## Example Queries to Try
- "Who are my riskiest customers?"
- "Which deals should I focus on today to hit my target?"
- "What's the status of the TechCorp deal?"
- "Summarize my overall pipeline health."
