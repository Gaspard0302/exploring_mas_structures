from typing import List, Dict, Any, Optional
import os

class Agent:
    def __init__(self, name: str, role: str, specialty: Optional[str] = None):
        self.name = name
        self.role = role
        self.specialty = specialty
        self.memory = []
        self.context = {}  # Context storage for agent state and knowledge

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

    def process(self, input_data: str) -> str:
        """Base process method to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement process method") 