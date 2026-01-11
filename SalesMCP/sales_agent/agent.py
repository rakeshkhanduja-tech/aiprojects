import os
import requests
import yaml
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser

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
        
        # Define schemas for structured output
        self.response_schemas = [
            ResponseSchema(name="tool_name", description="The name of the MCP tool to call"),
            ResponseSchema(name="parameters", description="Dictionary of parameters for the tool call (param or id)"),
            ResponseSchema(name="explanation", description="Why this tool is being called")
        ]
        self.output_parser = StructuredOutputParser.from_response_schemas(self.response_schemas)

    def get_available_tools(self):
        try:
            resp = requests.get(f"{self.mcp_base_url}/capabilities")
            return resp.json()['capabilities']
        except Exception as e:
            print(f"Error fetching capabilities: {e}")
            return []

    def translate_intent(self, question):
        tools = self.get_available_tools()
        format_instructions = self.output_parser.get_format_instructions()
        
        prompt = ChatPromptTemplate.from_template("""
            You are a Sales Assistant Intent Translator.
            Given a user question, decide which MCP tool from the list below is the best fit.
            
            Available Tools: {tools}
            
            User Question: {question}
            
            {format_instructions}
        """)
        
        messages = prompt.format_messages(
            tools=", ".join(tools),
            question=question,
            format_instructions=format_instructions
        )
        
        response = self.llm.invoke(messages)
        return self.output_parser.parse(response.content)

    def execute_query(self, question):
        # 1. Translate intent
        intent = self.translate_intent(question)
        tool_name = intent['tool_name']
        params = intent['parameters']
        
        # 2. Call MCP tool
        if tool_name == "log_agent_decision":
             return {"error": "Direct logging not allowed via NL query"}
             
        mcp_url = f"{self.mcp_base_url}/tools/{tool_name}"
        resp = requests.get(mcp_url, params=params)
        mcp_data = resp.json()
        
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
            explanation=intent['explanation']
        )
        
        recommendation_text = self.llm.invoke(messages).content
        
        # 4. Log the decision back to MCP
        # Parse confidence from text if possible, or use default
        decision_data = {
            "agent_name": "SalesGPT-MCP",
            "input_question": question,
            "recommendation": recommendation_text,
            "confidence": 0.9, # Simplified for demo
            "evidence": mcp_data
        }
        requests.post(f"{self.mcp_base_url}/log", json=decision_data)
        
        return {
            "recommendation": recommendation_text,
            "mcp_call": tool_name,
            "evidence": mcp_data
        }
