from openai import OpenAI
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Try to import config, fallback to environment variables
try:
    from config import get_openai_api_key, get_llm_config, get_evaluation_config
except ImportError:
    def get_openai_api_key():
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable or create config.py")
        return api_key
    
    def get_llm_config():
        return {"model": "gpt-4", "temperature": 0.7, "max_tokens": 1000}
    
    def get_evaluation_config():
        return {"log_dir": "logs", "results_dir": "results/llm_tsp", "cost_per_1k_tokens": 0.045}

@dataclass
class LLMCall:
    """Log entry for an LLM call"""
    timestamp: str
    agent_name: str
    agent_type: str  # 'leader', 'follower', 'peer', 'bidder', 'auctioneer'
    call_type: str   # 'reasoning', 'planning', 'negotiation', 'bidding', etc.
    prompt: str
    response: str
    context: Dict[str, Any]
    duration: float
    tokens_used: Optional[int] = None
    cost: Optional[float] = None

@dataclass 
class AgentCommunication:
    """Log entry for agent-to-agent communication"""
    timestamp: str
    sender: str
    receiver: str
    message_type: str  # 'task_assignment', 'negotiation', 'result_report', etc.
    content: str
    context: Dict[str, Any]

class LLMLogger:
    """Comprehensive logging system for LLM calls and agent communications"""
    
    def __init__(self, log_dir: str = None):
        eval_config = get_evaluation_config()
        self.log_dir = log_dir or eval_config["log_dir"]
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Separate logs for different types
        self.llm_calls: List[LLMCall] = []
        self.communications: List[AgentCommunication] = []
        
        # Session info
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.start_time = time.time()
        
        # Cost tracking
        self.cost_per_1k_tokens = eval_config["cost_per_1k_tokens"]
    
    def log_llm_call(self, agent_name: str, agent_type: str, call_type: str, 
                     prompt: str, response: str, context: Dict[str, Any], 
                     duration: float, tokens_used: Optional[int] = None) -> None:
        """Log an LLM API call"""
        call = LLMCall(
            timestamp=datetime.now().isoformat(),
            agent_name=agent_name,
            agent_type=agent_type,
            call_type=call_type,
            prompt=prompt,
            response=response,
            context=context,
            duration=duration,
            tokens_used=tokens_used,
            cost=self._estimate_cost(tokens_used) if tokens_used else None
        )
        self.llm_calls.append(call)
    
    def log_communication(self, sender: str, receiver: str, message_type: str, 
                          content: str, context: Dict[str, Any] = None) -> None:
        """Log agent-to-agent communication"""
        comm = AgentCommunication(
            timestamp=datetime.now().isoformat(),
            sender=sender,
            receiver=receiver,
            message_type=message_type,
            content=content,
            context=context or {}
        )
        self.communications.append(comm)
    
    def _estimate_cost(self, tokens: int) -> float:
        """Estimate cost based on configured pricing"""
        if not tokens:
            return 0.0
        return (tokens / 1000) * self.cost_per_1k_tokens
    
    def save_logs(self) -> Dict[str, str]:
        """Save all logs to files"""
        session_dir = os.path.join(self.log_dir, f"session_{self.session_id}")
        os.makedirs(session_dir, exist_ok=True)
        
        # Save LLM calls
        llm_file = os.path.join(session_dir, "llm_calls.json")
        with open(llm_file, 'w') as f:
            json.dump([asdict(call) for call in self.llm_calls], f, indent=2)
        
        # Save communications
        comm_file = os.path.join(session_dir, "communications.json")
        with open(comm_file, 'w') as f:
            json.dump([asdict(comm) for comm in self.communications], f, indent=2)
        
        # Save summary
        summary = self.get_session_summary()
        summary_file = os.path.join(session_dir, "session_summary.json")
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return {
            "session_dir": session_dir,
            "llm_calls": llm_file,
            "communications": comm_file,
            "summary": summary_file
        }
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary statistics for the session"""
        total_duration = time.time() - self.start_time
        
        llm_stats = {
            "total_calls": len(self.llm_calls),
            "total_tokens": sum(call.tokens_used or 0 for call in self.llm_calls),
            "total_cost": sum(call.cost or 0 for call in self.llm_calls),
            "total_llm_time": sum(call.duration for call in self.llm_calls),
            "calls_by_agent_type": {},
            "calls_by_type": {}
        }
        
        # Group by agent type and call type
        for call in self.llm_calls:
            agent_type = call.agent_type
            call_type = call.call_type
            
            if agent_type not in llm_stats["calls_by_agent_type"]:
                llm_stats["calls_by_agent_type"][agent_type] = 0
            llm_stats["calls_by_agent_type"][agent_type] += 1
            
            if call_type not in llm_stats["calls_by_type"]:
                llm_stats["calls_by_type"][call_type] = 0
            llm_stats["calls_by_type"][call_type] += 1
        
        comm_stats = {
            "total_messages": len(self.communications),
            "messages_by_type": {},
            "communication_patterns": {}
        }
        
        # Group communications
        for comm in self.communications:
            msg_type = comm.message_type
            if msg_type not in comm_stats["messages_by_type"]:
                comm_stats["messages_by_type"][msg_type] = 0
            comm_stats["messages_by_type"][msg_type] += 1
            
            # Track communication patterns (sender -> receiver)
            pattern = f"{comm.sender} -> {comm.receiver}"
            if pattern not in comm_stats["communication_patterns"]:
                comm_stats["communication_patterns"][pattern] = 0
            comm_stats["communication_patterns"][pattern] += 1
        
        return {
            "session_id": self.session_id,
            "total_duration": total_duration,
            "llm_statistics": llm_stats,
            "communication_statistics": comm_stats
        }

class LLMIntegration:
    """LLM integration for TSP agents using OpenAI 1.0+ API"""
    
    def __init__(self, api_key: str = None, model: str = None, logger: LLMLogger = None):
        # Get configuration
        llm_config = get_llm_config()
        
        # Set API key
        if not api_key:
            api_key = get_openai_api_key()
        
        # Set environment variable for OpenAI client
        os.environ["OPENAI_API_KEY"] = api_key
        
        # Initialize OpenAI client without explicit API key (uses env var)
        self.client = OpenAI()
        
        # Set model and other parameters
        self.model = model or llm_config["model"]
        self.temperature = llm_config["temperature"]
        self.max_tokens = llm_config["max_tokens"]
        self.logger = logger or LLMLogger()
    
    def call_llm(self, agent_name: str, agent_type: str, call_type: str, 
                 prompt: str, context: Dict[str, Any] = None) -> str:
        """Make an LLM call with logging"""
        start_time = time.time()
        context = context or {}
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            duration = time.time() - start_time
            response_text = response.choices[0].message.content.strip()
            tokens_used = response.usage.total_tokens
            
            # Log the call
            self.logger.log_llm_call(
                agent_name=agent_name,
                agent_type=agent_type,
                call_type=call_type,
                prompt=prompt,
                response=response_text,
                context=context,
                duration=duration,
                tokens_used=tokens_used
            )
            
            return response_text
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"LLM call failed: {str(e)}"
            
            # Log the failed call
            self.logger.log_llm_call(
                agent_name=agent_name,
                agent_type=agent_type,
                call_type=call_type,
                prompt=prompt,
                response=error_msg,
                context=context,
                duration=duration
            )
            
            return error_msg
    
    def log_communication(self, sender: str, receiver: str, message_type: str, 
                         content: str, context: Dict[str, Any] = None) -> None:
        """Log agent communication"""
        self.logger.log_communication(sender, receiver, message_type, content, context)

# Global logger instance
_global_logger = None

def get_logger() -> LLMLogger:
    """Get or create global logger instance"""
    global _global_logger
    if _global_logger is None:
        _global_logger = LLMLogger()
    return _global_logger

def get_llm_integration(api_key: str = None) -> LLMIntegration:
    """Get LLM integration with shared logger"""
    return LLMIntegration(api_key, logger=get_logger()) 