from typing import List, Dict, Any
import os
from dotenv import load_dotenv

class Agent:
    def __init__(self, name: str, role: str, tools: List = None):
        self.name = name
        self.role = role
        self.tools = tools or []
        self.memory = []
        self.context = {}  # MCP context storage

    def add_to_memory(self, message: str):
        """Add a message to the agent's memory"""
        self.memory.append(message)

    def get_memory(self) -> List[str]:
        """Retrieve the agent's memory"""
        return self.memory

    def update_context(self, key: str, value: Any) -> Dict:
        """Update the agent's context with new information"""
        self.context[key] = value
        return self.context

    def get_context(self, key: str = None) -> Any:
        """Retrieve context information"""
        if key:
            return self.context.get(key)
        return self.context

    def format_context_for_llm(self) -> str:
        """Format the context for LLM consumption"""
        formatted = "Current context:\n"
        for key, value in self.context.items():
            formatted += f"- {key}: {value}\n"
        return formatted

    def process_with_context(self, input_data: str) -> str:
        """Process input with awareness of current context"""
        context_prompt = self.format_context_for_llm()
        return f"Agent {self.name} processed with context: {input_data}" 