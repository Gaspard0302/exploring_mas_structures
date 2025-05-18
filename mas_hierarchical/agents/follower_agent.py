from typing import List, Dict, Any
from .base_agent import Agent

class FollowerAgent(Agent):
    def __init__(self, name: str, specialty: str):
        super().__init__(name, "Follower")
        self.specialty = specialty
        self.update_context("specialty", specialty)
        self.update_context("status", "idle")

    def process(self, task: str) -> str:
        """Process the assigned task"""
        self.add_to_memory(f"Received task: {task}")
        self.update_context("status", "working")
        self.update_context("current_task", task)

        # Simulate processing based on specialty and context
        objective = self.get_context("objective")
        specialty = self.get_context("specialty")

        # In a real implementation, you would use the context to inform processing
        result = f"Completed {task} with {specialty} specialty analysis"
        if objective:
            result += f" aligned with objective: {objective}"

        self.add_to_memory(f"Completed task with result: {result}")
        self.update_context("status", "completed")
        self.update_context("result", result)

        return result 