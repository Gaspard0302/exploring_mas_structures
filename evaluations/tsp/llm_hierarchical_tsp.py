from typing import List, Tuple, Dict, Any
import json
from .utils import TSPUtils
from .llm_integration import get_llm_integration, get_logger

def evaluate_llm_hierarchical_tsp(cities: List[Tuple[int, int]], n_agents: int, 
                                 api_key: str, seed: int = 42) -> Dict[str, Any]:
    """
    Evaluate Hierarchical MAS with LLM agents on TSP problem
    
    Args:
        cities: List of city coordinates
        n_agents: Number of follower agents (excluding leader)
        api_key: OpenAI API key
        seed: Random seed for reproducibility
    
    Returns:
        Dictionary with evaluation results and LLM logs
    """
    
    llm = get_llm_integration(api_key)
    logger = get_logger()
    
    # Step 1: Leader analyzes the problem and creates strategy
    leader_analysis_prompt = f"""
You are a LEADER agent coordinating a team of {n_agents} agents to solve a Traveling Salesman Problem.

PROBLEM:
- We have {len(cities)} cities to visit: {cities}
- We have {n_agents} agents available
- Goal: Minimize total travel distance across all agents

YOUR TASK:
1. Analyze the city layout and identify geographical clusters
2. Decide how to partition cities among {n_agents} agents for optimal efficiency
3. Create a coordination strategy

Think step by step:
1. What patterns do you see in the city coordinates?
2. How would you group cities to minimize overlap and travel distance?
3. What instructions should each agent receive?

Respond with:
1. Your analysis of the city layout
2. Proposed city clusters (as lists of city indices)
3. Strategy for coordination

Format your response as JSON:
{{
    "analysis": "your analysis here",
    "clusters": [[city_indices_for_agent_0], [city_indices_for_agent_1], ...],
    "coordination_strategy": "your strategy description"
}}
"""
    
    leader_response = llm.call_llm(
        agent_name="Leader",
        agent_type="leader", 
        call_type="strategic_planning",
        prompt=leader_analysis_prompt,
        context={"cities": cities, "n_agents": n_agents}
    )
    
    # Parse leader's response
    try:
        leader_decision = json.loads(leader_response)
        clusters = leader_decision.get("clusters", [])
        strategy = leader_decision.get("coordination_strategy", "")
    except json.JSONDecodeError:
        # Fallback to algorithmic clustering if LLM response isn't parseable
        cluster_dict = TSPUtils.cluster_cities(cities, n_agents, seed=seed)
        clusters = [cluster_dict[i] for i in range(len(cluster_dict))]
        strategy = "Fallback to algorithmic clustering due to parsing error"
    
    # Log leader's coordination
    llm.log_communication(
        sender="Leader",
        receiver="All_Agents",
        message_type="strategic_plan",
        content=f"Strategy: {strategy}",
        context={"clusters": clusters}
    )
    
    # Step 2: Assign tasks to follower agents with LLM reasoning
    agent_assignments = {}
    agent_routes = {}
    agent_distances = {}
    agent_loads = []
    total_distance = 0
    
    for i in range(min(len(clusters), n_agents)):
        agent_name = f"Follower_{i}"
        city_indices = clusters[i] if i < len(clusters) else []
        
        if not city_indices:
            agent_loads.append(0)
            agent_routes[agent_name] = []
            agent_distances[agent_name] = 0
            continue
            
        agent_cities = [cities[j] for j in city_indices]
        agent_loads.append(len(agent_cities))
        
        # Log task assignment
        llm.log_communication(
            sender="Leader",
            receiver=agent_name,
            message_type="task_assignment",
            content=f"Handle cities: {city_indices}",
            context={"cities": agent_cities}
        )
        
        # Agent reasons about their route
        agent_prompt = f"""
You are AGENT {agent_name} with expertise in route optimization.

ASSIGNMENT:
Your leader has assigned you these {len(agent_cities)} cities to visit:
"""
        
        # Add clear city mapping
        for idx, (x, y) in enumerate(agent_cities):
            agent_prompt += f"  City {idx}: position ({x}, {y})\n"
        
        agent_prompt += f"""
IMPORTANT: You are working with LOCAL indices 0, 1, 2, ..., {len(agent_cities)-1} for your assigned cities.

TASK:
Plan the optimal route through your assigned cities to minimize travel distance.

Consider:
1. Which city should you start from? (use local index 0-{len(agent_cities)-1})
2. What's the most efficient order to visit all cities?
3. How would you optimize this route to minimize total distance?

Think through different route options and explain your reasoning.

EXAMPLE:
If you have 3 cities [City 0, City 1, City 2], a good route might be [0, 2, 1] meaning:
visit City 0 first, then City 2, then City 1.

Respond EXACTLY in this JSON format:
{{
    "reasoning": "your step-by-step reasoning about the optimal route",
    "route": [list_of_local_indices_from_0_to_{len(agent_cities)-1}],
    "estimated_distance": your_distance_estimate
}}

CRITICAL: The route array must contain exactly {len(agent_cities)} integers, each between 0 and {len(agent_cities)-1}, with no duplicates.
"""
        
        agent_response = llm.call_llm(
            agent_name=agent_name,
            agent_type="follower",
            call_type="route_planning",
            prompt=agent_prompt,
            context={"assigned_cities": city_indices, "coordinates": agent_cities, "local_city_count": len(agent_cities)}
        )
        
        # Parse agent's route decision with improved error handling
        try:
            agent_decision = json.loads(agent_response)
            planned_route = agent_decision.get("route", list(range(len(city_indices))))
            reasoning = agent_decision.get("reasoning", "No reasoning provided")
            
            # Debug: Print what we received
            print(f"Debug: Agent {agent_name} returned route: {planned_route} for {len(city_indices)} cities")
            
        except json.JSONDecodeError:
            # Fallback to algorithmic route
            planned_route, _ = TSPUtils.nearest_neighbor_tsp(agent_cities)
            reasoning = "Fallback to algorithmic routing due to parsing error"
            print(f"Debug: Agent {agent_name} JSON parsing failed, using algorithmic route: {planned_route}")
        
        # Improved validation and conversion logic
        global_route = city_indices  # Default fallback
        route_valid = False
        
        if isinstance(planned_route, list) and len(planned_route) == len(city_indices):
            # Check if it's already local indices (expected format)
            if all(isinstance(x, int) and 0 <= x < len(city_indices) for x in planned_route):
                # Check for duplicates (should be a permutation)
                if len(set(planned_route)) == len(planned_route):
                    global_route = [city_indices[j] for j in planned_route]
                    route_valid = True
                    print(f"Debug: Agent {agent_name} returned valid local indices: {planned_route}")
                else:
                    print(f"Debug: Agent {agent_name} returned duplicate indices: {planned_route}")
            
            # Check if it might be global indices matching our assigned cities
            elif all(isinstance(x, int) and x in city_indices for x in planned_route):
                # Reorder to match the sequence they want
                if len(set(planned_route)) == len(planned_route):  # No duplicates
                    global_route = planned_route
                    route_valid = True
                    print(f"Debug: Agent {agent_name} returned valid global indices: {planned_route}")
                else:
                    print(f"Debug: Agent {agent_name} returned duplicate global indices: {planned_route}")
            else:
                print(f"Debug: Agent {agent_name} returned invalid indices: {planned_route} (expected 0-{len(city_indices)-1} or {city_indices})")
        else:
            print(f"Debug: Agent {agent_name} returned wrong format - expected list of {len(city_indices)} integers, got: {planned_route}")
        
        if not route_valid:
            print(f"Warning: Agent {agent_name} returned invalid route format, using original order")
            print(f"  Expected: local indices 0-{len(city_indices)-1} or global indices {city_indices}")
            print(f"  Received: {planned_route}")
        
        # Calculate actual distance
        if len(agent_cities) <= 1:
            actual_distance = 0
        else:
            # Calculate distance based on the final global route
            if route_valid and isinstance(planned_route, list) and len(planned_route) == len(agent_cities):
                # If we have valid local indices, use them to reorder agent_cities
                if all(isinstance(x, int) and 0 <= x < len(agent_cities) for x in planned_route):
                    route_cities = [agent_cities[j] for j in planned_route]
                    actual_distance = TSPUtils.calculate_route_distance(route_cities, list(range(len(route_cities))))
                    print(f"Debug: Agent {agent_name} distance calculated from optimized route: {actual_distance:.2f}")
                else:
                    # Fallback to original order
                    actual_distance = TSPUtils.calculate_route_distance(agent_cities, list(range(len(agent_cities))))
                    print(f"Debug: Agent {agent_name} distance calculated from original order: {actual_distance:.2f}")
            else:
                # Fallback to using cities in original order
                actual_distance = TSPUtils.calculate_route_distance(agent_cities, list(range(len(agent_cities))))
                print(f"Debug: Agent {agent_name} distance calculated from fallback order: {actual_distance:.2f}")
        
        agent_assignments[agent_name] = city_indices
        agent_routes[agent_name] = global_route
        agent_distances[agent_name] = actual_distance
        total_distance += actual_distance
        
        # Log agent's result back to leader
        llm.log_communication(
            sender=agent_name,
            receiver="Leader",
            message_type="task_completion",
            content=f"Route planned with distance {actual_distance:.2f}. Reasoning: {reasoning}",
            context={"route": global_route, "distance": actual_distance}
        )
    
    # Step 3: Leader synthesizes final coordination
    final_synthesis_prompt = f"""
You are the LEADER agent receiving completion reports from your team.

TEAM RESULTS:
"""
    
    for agent_name, distance in agent_distances.items():
        route = agent_routes[agent_name]
        final_synthesis_prompt += f"- {agent_name}: Route {route}, Distance: {distance:.2f}\n"
    
    final_synthesis_prompt += f"""
TOTAL DISTANCE: {total_distance:.2f}

As the leader, evaluate:
1. How well did the team perform?
2. What coordination patterns emerged?
3. Could the city partitioning be improved?
4. What insights do you have about hierarchical coordination for this problem?

Provide your final assessment and insights about team coordination.
"""
    
    leader_synthesis = llm.call_llm(
        agent_name="Leader",
        agent_type="leader",
        call_type="final_synthesis",
        prompt=final_synthesis_prompt,
        context={
            "total_distance": total_distance,
            "agent_results": agent_distances,
            "coordination_effectiveness": len([d for d in agent_distances.values() if d > 0])
        }
    )
    
    # Additional metrics
    communication_overhead = len(logger.communications)
    
    # Calculate clustering efficiency if we have valid clusters
    clustering_efficiency = 0
    if clusters and len([c for c in clusters if c]):  # Check if we have non-empty clusters
        total_intra_distance = 0
        total_pairs = 0
        for cluster in clusters:
            if len(cluster) < 2:
                continue
            for i in range(len(cluster)):
                for j in range(i + 1, len(cluster)):
                    city1 = cities[cluster[i]]
                    city2 = cities[cluster[j]]
                    total_intra_distance += TSPUtils.calculate_distance(city1, city2)
                    total_pairs += 1
        clustering_efficiency = total_intra_distance / total_pairs if total_pairs > 0 else 0
    
    additional_metrics = {
        'clustering_efficiency': clustering_efficiency,
        'leader_coordination_overhead': n_agents + 1,
        'agent_distances': agent_distances,
        'coordination_quality': leader_synthesis,
        'llm_calls': len(logger.llm_calls),
        'total_tokens': sum(call.tokens_used or 0 for call in logger.llm_calls),
        'total_llm_cost': sum(call.cost or 0 for call in logger.llm_calls)
    }
    
    return {
        'total_distance': total_distance,
        'communication_overhead': communication_overhead,
        'agent_loads': agent_loads,
        'agent_routes': agent_routes,
        'agent_assignments': agent_assignments,
        'clusters': clusters,
        'additional_metrics': additional_metrics
    } 