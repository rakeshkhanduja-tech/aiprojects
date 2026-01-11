import os
import requests
import yaml
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

class Intent(BaseModel):
    """The intent of the user's question, mapped to an MCP tool."""
    tool_name: str = Field(description="The name of the MCP tool to call")
    parameters: Dict[str, Any] = Field(description="Dictionary of parameters for the tool call (param or id)")
    explanation: str = Field(description="Why this tool is being called")

class SalesAgent:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            full_config = yaml.safe_load(f)
            self.mcp_config = full_config['mcp']
            self.agent_config = full_config['agent']
        
        self.mcp_base_url = f"http://{self.mcp_config['host']}:{self.mcp_config['port']}"
        self.llm = ChatGoogleGenerativeAI(
            model=self.agent_config['model'],
            temperature=self.agent_config['temperature']
        )
        # Modern structured output
        self.intent_analyzer = self.llm.with_structured_output(Intent)

    def get_available_tools(self) -> List[str]:
        try:
            resp = requests.get(f"{self.mcp_base_url}/capabilities")
            return resp.json()['capabilities']
        except Exception as e:
            print(f"Error fetching capabilities: {e}")
            return []

    def translate_intent(self, question: str) -> Intent:
        tools = self.get_available_tools()
        
        prompt = ChatPromptTemplate.from_template("""
            You are a Sales Assistant Intent Translator.
            Given a user question, decide which MCP tool from the list below is the best fit.
            
            Available Tools: {tools}
            
            User Question: {question}
        """)
        
        chain = prompt | self.intent_analyzer
        return chain.invoke({"tools": ", ".join(tools), "question": question})

    def execute_query(self, question: str) -> Dict[str, Any]:
        # 1. Translate intent
        intent = self.translate_intent(question)
        tool_name = intent.tool_name
        params = intent.parameters
        
        # 2. Call MCP tool
        if tool_name == "log_agent_decision":
             return {"error": "Direct logging not allowed via NL query"}
             
        mcp_url = f"{self.mcp_base_url}/tools/{tool_name}"
        try:
            resp = requests.get(mcp_url, params=params)
            resp.raise_for_status()
            mcp_data = resp.json()
        except Exception as e:
            return {"error": f"MCP Tool Call Failed: {str(e)}", "mcp_call": tool_name}
        
        # 3. Generate final recommendation
        prompt = ChatPromptTemplate.from_template("""
            You are a Senior Sales Operations Advisor.
            
            User Question: {question}
            MCP Data: {mcp_data}
            Agent Reasoning for data selection: {explanation}
            
            Produce a clear, professional B2B sales recommendation.
            Include:
            1. Recommendation
            2. Confidence Score (0.0 to 1.0)
            3. Detailed Explanation
            4. Evidence Summary (bullet points of data used)
            
            Format as Markdown.
        """)
        
        messages = prompt.format_messages(
            question=question,
            mcp_data=str(mcp_data),
            explanation=intent.explanation
        )
        
        recommendation_text = self.llm.invoke(messages).content
        
        # 4. Log the decision back to MCP
        decision_data = {
            "agent_name": "SalesGPT-MCP",
            "input_question": question,
            "recommendation": recommendation_text,
            "confidence": 0.9,
            "evidence": mcp_data
        }
        try:
            requests.post(f"{self.mcp_base_url}/log", json=decision_data)
        except:
            pass # Don't fail if audit logging fails
        
        return {
            "recommendation": recommendation_text,
            "mcp_call": tool_name,
            "evidence": mcp_data
        }
