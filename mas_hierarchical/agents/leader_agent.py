from typing import List, Dict, Any
from .base_agent import Agent

class LeaderAgent(Agent):
    def __init__(self, name: str, followers: List = None):
        super().__init__(name, "Leader")
        self.followers = followers or []
        self.plan = []
        # Initialize with MCP context
        self.update_context("objective", None)
        self.update_context("plan_status", "not_started")
        self.update_context("team_status", {})

    def add_follower(self, follower: Agent):
        """Add a follower agent to the team"""
        self.followers.append(follower)
        # Update team context
        team_status = self.get_context("team_status")
        team_status[follower.name] = {
            "status": "idle",
            "specialty": getattr(follower, 'specialty', 'general')
        }
        self.update_context("team_status", team_status)

    def create_plan(self, objective: str) -> List[str]:
        """Create a plan based on the objective"""
        self.update_context("objective", objective)
        self.update_context("plan_status", "planning")

        # Create plan based on context
        self.plan = [
            f"Step 1: Analyze objective: {objective}",
            "Step 2: Divide tasks among followers",
            "Step 3: Collect results from followers",
            "Step 4: Synthesize final solution"
        ]

        self.update_context("plan", self.plan)
        self.update_context("plan_status", "planned")
        return self.plan

    def assign_tasks(self) -> Dict[str, str]:
        """Assign tasks to followers"""
        self.update_context("plan_status", "assigning_tasks")

        tasks = {}
        team_status = self.get_context("team_status")

        for i, follower in enumerate(self.followers):
            task = f"Task {i+1}: Perform analysis on section {i+1}"
            tasks[follower.name] = task

            # Update follower status in context
            team_status[follower.name]["status"] = "assigned"
            team_status[follower.name]["current_task"] = task

        self.update_context("team_status", team_status)
        self.update_context("tasks", tasks)
        return tasks

    def process(self, objective: str) -> str:
        """Process the objective and coordinate the team"""
        self.add_to_memory(f"Received objective: {objective}")
        plan = self.create_plan(objective)
        self.add_to_memory(f"Created plan: {plan}")

        tasks = self.assign_tasks()
        self.add_to_memory(f"Assigned tasks: {tasks}")

        self.update_context("plan_status", "executing")
        results = {}
        team_status = self.get_context("team_status")

        for follower in self.followers:
            # Share relevant context with follower
            follower.update_context("objective", self.get_context("objective"))
            follower.update_context("assigned_task", tasks[follower.name])

            # Process task
            task = tasks[follower.name]
            result = follower.process(task)
            results[follower.name] = result

            # Update follower status
            team_status[follower.name]["status"] = "completed"
            team_status[follower.name]["result"] = result

        self.update_context("team_status", team_status)
        self.update_context("results", results)
        self.update_context("plan_status", "synthesizing")

        # Synthesize final solution
        final_result = f"Final solution for objective '{objective}':\n"
        for agent_name, result in results.items():
            final_result += f"- {agent_name}: {result}\n"

        self.add_to_memory(f"Synthesized final solution")
        self.update_context("plan_status", "completed")
        self.update_context("final_result", final_result)

        return final_result 