from typing import List, Dict, Any, Optional, Set
from .base_agent import Agent
import os
import json

class PeerAgent(Agent):
    def __init__(self, name: str, specialty: str):
        super().__init__(name, "Peer", specialty)
        self.peers = {}  # Dict of peer agents this agent can communicate with
        self.messages = []  # Message queue
        self.update_context("status", "idle")
        self.update_context("specialty", specialty)
        self.knowledge_base = {}  # Local knowledge base for agent

    def add_peer(self, peer_agent: 'PeerAgent'):
        """Add a peer agent to this agent's network"""
        if peer_agent.name != self.name:  # Don't add self as peer
            self.peers[peer_agent.name] = peer_agent
            self.add_to_memory(f"Added peer: {peer_agent.name} with specialty: {peer_agent.specialty}")

    def remove_peer(self, peer_name: str):
        """Remove a peer agent from this agent's network"""
        if peer_name in self.peers:
            del self.peers[peer_name]
            self.add_to_memory(f"Removed peer: {peer_name}")

    def send_message(self, peer_name: str, message: str) -> bool:
        """Send a message to a peer agent"""
        if peer_name in self.peers:
            self.add_to_memory(f"Sending message to {peer_name}: {message}")
            return self.peers[peer_name].receive_message(self.name, message)
        else:
            self.add_to_memory(f"Failed to send message to unknown peer: {peer_name}")
            return False

    def receive_message(self, sender_name: str, message: str) -> bool:
        """Receive a message from another agent"""
        self.messages.append({"sender": sender_name, "message": message})
        self.add_to_memory(f"Received message from {sender_name}: {message}")
        return True

    def get_messages(self, clear: bool = False) -> List[Dict]:
        """Get all messages received by this agent"""
        messages = self.messages.copy()
        if clear:
            self.messages = []
        return messages

    def process(self, task: str) -> str:
        """Process the given task based on agent's specialty"""
        self.add_to_memory(f"Processing task: {task}")
        self.update_context("status", "working")
        self.update_context("current_task", task)

        # Process the task based on specialty
        result = f"Agent {self.name} with {self.specialty} specialty processed: {task}"
        
        # Update status and knowledge
        self.update_context("status", "completed")
        self.update_context("result", result)
        self.add_to_memory(f"Task completed with result: {result}")
        
        return result

    def collaborate(self, task: str, required_specialties: List[str] = None) -> str:
        """Collaborate with peers to solve a complex task"""
        self.add_to_memory(f"Starting collaboration on task: {task}")
        self.update_context("status", "collaborating")
        
        # Identify which peers to collaborate with based on required specialties
        collaboration_peers = []
        if required_specialties:
            for peer_name, peer in self.peers.items():
                if peer.specialty in required_specialties:
                    collaboration_peers.append(peer_name)
        else:
            # If no specific specialties required, collaborate with all peers
            collaboration_peers = list(self.peers.keys())
        
        # Send collaboration requests
        for peer_name in collaboration_peers:
            self.send_message(peer_name, f"Collaboration request: {task}")
        
        # Process own part of the task
        own_result = self.process(f"Own contribution to: {task}")
        
        # In a real implementation, would wait for and process peer responses
        # For now, just simulate responses
        peer_results = []
        for peer_name in collaboration_peers:
            peer_results.append(f"{peer_name}: Simulated contribution to {task}")
        
        # Combine results
        final_result = f"Collaboration results for '{task}':\n"
        final_result += f"- {self.name} (self): {own_result}\n"
        for result in peer_results:
            final_result += f"- {result}\n"
        
        self.update_context("status", "completed")
        self.add_to_memory(f"Collaboration completed with combined results")
        
        return final_result

    def update_knowledge(self, key: str, value: Any):
        """Update the agent's knowledge base"""
        self.knowledge_base[key] = value
        self.add_to_memory(f"Updated knowledge: {key}")

    def share_knowledge(self, peer_names: List[str] = None) -> int:
        """Share knowledge with specific peers or all peers"""
        if not peer_names:
            peer_names = list(self.peers.keys())
        
        shares_count = 0
        knowledge_json = json.dumps(self.knowledge_base)
        
        for peer_name in peer_names:
            if peer_name in self.peers:
                self.send_message(peer_name, f"KNOWLEDGE_SHARE:{knowledge_json}")
                shares_count += 1
        
        self.add_to_memory(f"Shared knowledge with {shares_count} peers")
        return shares_count

    def get_network_info(self) -> Dict:
        """Get information about this agent's peer network"""
        return {
            "agent": self.name,
            "specialty": self.specialty,
            "peers_count": len(self.peers),
            "peers": [{"name": name, "specialty": peer.specialty} 
                     for name, peer in self.peers.items()]
        } 