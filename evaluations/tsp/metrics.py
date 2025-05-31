import time
import statistics
from typing import Dict, List, Any
from dataclasses import dataclass, field

@dataclass
class TSPMetrics:
    """Class to collect and analyze TSP performance metrics"""
    architecture: str
    total_distance: float = 0.0
    computation_time: float = 0.0
    communication_overhead: int = 0
    agent_loads: List[int] = field(default_factory=list)
    agent_routes: Dict[str, List[int]] = field(default_factory=dict)
    additional_metrics: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_load_balance_variance(self) -> float:
        """Calculate variance in load distribution among agents"""
        if len(self.agent_loads) < 2:
            return 0.0
        return statistics.variance(self.agent_loads)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        return {
            "architecture": self.architecture,
            "total_distance": round(self.total_distance, 2),
            "computation_time": round(self.computation_time, 4),
            "communication_overhead": self.communication_overhead,
            "load_balance_variance": round(self.calculate_load_balance_variance(), 2),
            "agents_count": len(self.agent_loads),
            "avg_cities_per_agent": round(statistics.mean(self.agent_loads), 2) if self.agent_loads else 0,
            "additional_metrics": self.additional_metrics
        }

class TSPEvaluator:
    """Evaluator for TSP multi-agent systems"""
    
    def __init__(self):
        self.results = []
    
    def evaluate_mas(self, mas_type: str, cities: List[tuple], n_agents: int, 
                    evaluation_func, **kwargs) -> TSPMetrics:
        """Evaluate a MAS architecture on TSP"""
        start_time = time.time()
        
        # Run the MAS-specific evaluation
        result = evaluation_func(cities, n_agents, **kwargs)
        
        end_time = time.time()
        computation_time = end_time - start_time
        
        # Create metrics object
        metrics = TSPMetrics(
            architecture=mas_type,
            total_distance=result.get('total_distance', 0),
            computation_time=computation_time,
            communication_overhead=result.get('communication_overhead', 0),
            agent_loads=result.get('agent_loads', []),
            agent_routes=result.get('agent_routes', {}),
            additional_metrics=result.get('additional_metrics', {})
        )
        
        self.results.append(metrics)
        return metrics
    
    def compare_architectures(self) -> Dict[str, Any]:
        """Compare performance across different MAS architectures"""
        if not self.results:
            return {}
        
        comparison = {}
        
        for metric in self.results:
            arch = metric.architecture
            comparison[arch] = metric.get_summary()
        
        # Add relative performance analysis
        distances = [m.total_distance for m in self.results]
        times = [m.computation_time for m in self.results]
        communications = [m.communication_overhead for m in self.results]
        variances = [m.calculate_load_balance_variance() for m in self.results]
        
        comparison['performance_analysis'] = {
            'best_distance': min(distances),
            'fastest_computation': min(times),
            'lowest_communication': min(communications),
            'best_load_balance': min(variances),
            'distance_range': max(distances) - min(distances),
            'time_range': max(times) - min(times)
        }
        
        return comparison 