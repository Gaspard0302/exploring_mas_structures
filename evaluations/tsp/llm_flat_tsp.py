from typing import List, Tuple, Dict, Any
import json
import random
from .utils import TSPUtils
from .llm_integration import get_llm_integration, get_logger

def evaluate_llm_flat_tsp(cities: List[Tuple[int, int]], n_agents: int, 
                         api_key: str, seed: int = 42, max_negotiation_rounds: int = 3) -> Dict[str, Any]:
    """
    Evaluate Flat MAS with LLM agents negotiating peer-to-peer on TSP
    
    Args:
        cities: List of city coordinates
        n_agents: Number of peer agents
        api_key: OpenAI API key
        seed: Random seed for reproducibility
        max_negotiation_rounds: Maximum rounds of negotiation
    
    Returns:
        Dictionary with evaluation results and LLM logs
    """
    
    random.seed(seed)
    llm = get_llm_integration(api_key)
    logger = get_logger()
    
    # Initialize agents with specialties and starting perspectives
    agent_names = [f"Agent_{i}" for i in range(n_agents)]
    agent_specialties = [
        "Geometric Optimization", "Efficiency Analysis", "Spatial Reasoning", 
        "Distance Minimization", "Route Planning", "Cost Analysis"
    ][:n_agents]
    
    # Initialize empty assignments
    agent_assignments = {name: [] for name in agent_names}
    unassigned_cities = list(range(len(cities)))
    
    # Step 1: Initial assessment by each agent
    for i, agent_name in enumerate(agent_names):
        specialty = agent_specialties[i]
        
        assessment_prompt = f"""
You are {agent_name}, a peer agent specializing in {specialty} working with {n_agents-1} other agents to solve a collaborative TSP.

PROBLEM OVERVIEW:
- Cities to visit: {cities}
- Total cities: {len(cities)}
- Your team size: {n_agents} agents (including you)
- Goal: Collaborate to minimize total travel distance

YOUR SPECIALTY: {specialty}

TASK: Analyze the problem from your expertise perspective and propose an initial strategy.

Consider:
1. How should cities be distributed among agents?
2. What patterns do you see that align with your specialty?
3. Which cities would you prefer to handle and why?
4. What collaboration approach do you suggest?

Format your response as JSON:
{{
    "analysis": "your analysis of the problem",
    "preferred_cities": [list_of_city_indices_you_want],
    "reasoning": "why you want these specific cities",
    "collaboration_proposal": "how you suggest working with peers"
}}
"""
        
        agent_response = llm.call_llm(
            agent_name=agent_name,
            agent_type="peer",
            call_type="initial_assessment",
            prompt=assessment_prompt,
            context={"specialty": specialty, "cities": cities, "n_agents": n_agents}
        )
        
        # Parse response for initial preferences
        try:
            assessment = json.loads(agent_response)
            preferred_cities = assessment.get("preferred_cities", [])
            reasoning = assessment.get("reasoning", "No reasoning provided")
        except json.JSONDecodeError:
            preferred_cities = []
            reasoning = "Parsing error in assessment"
        
        # Log initial assessment
        llm.log_communication(
            sender=agent_name,
            receiver="All_Peers",
            message_type="initial_assessment",
            content=f"Specialty: {specialty}. Preferred cities: {preferred_cities}. Reasoning: {reasoning}",
            context={"specialty": specialty, "preferred_cities": preferred_cities}
        )
    
    # Step 2: Negotiation rounds
    for round_num in range(max_negotiation_rounds):
        if not unassigned_cities:
            break
            
        # Each agent proposes claims for this round
        round_claims = {}
        
        for agent_name in agent_names:
            current_cities = agent_assignments[agent_name]
            
            negotiation_prompt = f"""
You are {agent_name} in negotiation round {round_num + 1} of {max_negotiation_rounds}.

CURRENT SITUATION:
- Your current cities: {current_cities}
- Remaining unassigned cities: {unassigned_cities}
- Cities coordinates: {cities}

PEER ASSIGNMENTS SO FAR:"""
            
            for peer_name, peer_cities in agent_assignments.items():
                if peer_name != agent_name:
                    negotiation_prompt += f"\n- {peer_name}: {peer_cities}"
            
            negotiation_prompt += f"""

YOUR TASK: Negotiate for additional cities to add to your route.

Consider:
1. Which unassigned cities would best extend your current route?
2. How can you argue for these cities based on efficiency?
3. What would be fair given your peers' current assignments?
4. Which cities should you prioritize this round?

Respond with:
1. Cities you want to claim this round (maximum 3)
2. Your argument for why you should get these cities
3. Any concessions or collaborative proposals

Format as JSON:
{{
    "claimed_cities": [list_of_city_indices_to_claim],
    "argument": "your argument for claiming these cities",
    "collaborative_notes": "any proposals or concessions for peers"
}}
"""
            
            claim_response = llm.call_llm(
                agent_name=agent_name,
                agent_type="peer",
                call_type="negotiation_claim",
                prompt=negotiation_prompt,
                context={
                    "round": round_num,
                    "current_cities": current_cities,
                    "unassigned": unassigned_cities,
                    "peer_assignments": agent_assignments
                }
            )
            
            # Parse claims
            try:
                claim_data = json.loads(claim_response)
                claimed_cities = claim_data.get("claimed_cities", [])
                argument = claim_data.get("argument", "No argument provided")
                collaboration = claim_data.get("collaborative_notes", "")
            except json.JSONDecodeError:
                claimed_cities = []
                argument = "Parsing error in claim"
                collaboration = ""
            
            # Filter valid claims (only unassigned cities)
            valid_claims = [c for c in claimed_cities if c in unassigned_cities][:3]  # Max 3 per round
            round_claims[agent_name] = {
                "claims": valid_claims,
                "argument": argument,
                "collaboration": collaboration
            }
            
            # Log the claim
            llm.log_communication(
                sender=agent_name,
                receiver="All_Peers",
                message_type="negotiation_claim",
                content=f"Round {round_num + 1}: Claiming cities {valid_claims}. Argument: {argument}",
                context={"round": round_num, "claims": valid_claims, "argument": argument}
            )
        
        # Step 3: Conflict resolution through peer discussion
        conflicts = {}
        for city in unassigned_cities:
            claimants = [agent for agent, data in round_claims.items() if city in data["claims"]]
            if len(claimants) > 1:
                conflicts[city] = claimants
        
        # Resolve conflicts through LLM mediation
        resolved_assignments = {}
        
        if conflicts:
            # Group discussion for each conflict
            for city, claimants in conflicts.items():
                conflict_prompt = f"""
CONFLICT RESOLUTION - City {city} at coordinates {cities[city]}

Multiple agents want this city:
"""
                for claimant in claimants:
                    claim_data = round_claims[claimant]
                    conflict_prompt += f"- {claimant}: {claim_data['argument']}\n"
                
                conflict_prompt += f"""
You are mediating this conflict. Consider:
1. Which agent has the strongest case based on efficiency?
2. Who would this city fit best with given their current assignments?
3. How can we maintain fairness across all agents?

Current assignments:"""
                for agent_name, cities_assigned in agent_assignments.items():
                    conflict_prompt += f"\n- {agent_name}: {len(cities_assigned)} cities"
                
                conflict_prompt += f"""

Decide who should get city {city} and provide reasoning.

Format as JSON:
{{
    "winner": "agent_name",
    "reasoning": "explanation for the decision"
}}
"""
                
                resolution = llm.call_llm(
                    agent_name="Mediator",
                    agent_type="mediator",
                    call_type="conflict_resolution",
                    prompt=conflict_prompt,
                    context={"city": city, "claimants": claimants, "assignments": agent_assignments}
                )
                
                try:
                    resolution_data = json.loads(resolution)
                    winner = resolution_data.get("winner", random.choice(claimants))
                    reasoning = resolution_data.get("reasoning", "Random selection")
                except json.JSONDecodeError:
                    winner = random.choice(claimants)
                    reasoning = "Fallback to random selection"
                
                if winner in claimants:
                    resolved_assignments[city] = winner
                    
                    # Log resolution
                    llm.log_communication(
                        sender="Mediator",
                        receiver="All_Peers",
                        message_type="conflict_resolution",
                        content=f"City {city} assigned to {winner}. Reasoning: {reasoning}",
                        context={"city": city, "winner": winner, "claimants": claimants}
                    )
        
        # Assign uncontested cities
        for agent_name, claim_data in round_claims.items():
            for city in claim_data["claims"]:
                if city not in conflicts:
                    resolved_assignments[city] = agent_name
        
        # Update assignments and remove assigned cities
        for city, winner in resolved_assignments.items():
            agent_assignments[winner].append(city)
            unassigned_cities.remove(city)
    
    # Assign any remaining cities randomly
    for city in unassigned_cities:
        agent_name = random.choice(agent_names)
        agent_assignments[agent_name].append(city)
    
    # Step 4: Each agent optimizes their final route with LLM reasoning
    agent_routes = {}
    agent_distances = {}
    total_distance = 0
    agent_loads = []
    
    for agent_name in agent_names:
        city_indices = agent_assignments[agent_name]
        agent_loads.append(len(city_indices))
        
        if not city_indices:
            agent_routes[agent_name] = []
            agent_distances[agent_name] = 0
            continue
        
        agent_cities = [cities[i] for i in city_indices]
        
        route_optimization_prompt = f"""
You are {agent_name} finalizing your route through your assigned cities.

FINAL ASSIGNMENT: {city_indices}
City coordinates: {agent_cities}

TASK: Determine the optimal order to visit your cities to minimize travel distance.

Analyze:
1. Different possible starting points
2. Various route sequences
3. Travel distances between cities
4. Most efficient path overall

Provide your optimized route as city indices in visit order.

Format as JSON:
{{
    "analysis": "your route optimization analysis",
    "optimal_route": [ordered_list_of_city_indices],
    "estimated_distance": your_estimated_total_distance
}}
"""
        
        route_response = llm.call_llm(
            agent_name=agent_name,
            agent_type="peer",
            call_type="route_optimization",
            prompt=route_optimization_prompt,
            context={"assigned_cities": city_indices, "coordinates": agent_cities}
        )
        
        # Parse route
        try:
            route_data = json.loads(route_response)
            planned_route = route_data.get("optimal_route", city_indices)
            analysis = route_data.get("analysis", "No analysis provided")
        except json.JSONDecodeError:
            planned_route = city_indices
            analysis = "Fallback route due to parsing error"
        
        # Calculate actual distance
        if len(agent_cities) <= 1:
            actual_distance = 0
        else:
            # Use the planned route if valid, otherwise use nearest neighbor
            if (len(planned_route) == len(city_indices) and 
                set(planned_route) == set(city_indices) and
                all(isinstance(x, int) for x in planned_route)):
                route_cities = [cities[i] for i in planned_route]
                actual_distance = TSPUtils.calculate_route_distance(route_cities, list(range(len(route_cities))))
            else:
                print(f"Warning: Agent {agent_name} returned invalid route, using nearest neighbor fallback")
                route, actual_distance = TSPUtils.nearest_neighbor_tsp(agent_cities)
                planned_route = [city_indices[i] for i in route]
        
        agent_routes[agent_name] = planned_route
        agent_distances[agent_name] = actual_distance
        total_distance += actual_distance
        
        # Log final route
        llm.log_communication(
            sender=agent_name,
            receiver="All_Peers",
            message_type="final_route",
            content=f"Final route: {planned_route}, Distance: {actual_distance:.2f}. Analysis: {analysis}",
            context={"route": planned_route, "distance": actual_distance}
        )
    
    # Calculate metrics
    communication_overhead = len(logger.communications)
    
    # Calculate load fairness
    mean_load = sum(agent_loads) / len(agent_loads) if agent_loads else 0
    load_variance = sum((load - mean_load) ** 2 for load in agent_loads) / len(agent_loads) if agent_loads else 0
    load_fairness = (load_variance ** 0.5) / mean_load if mean_load > 0 else 0
    
    additional_metrics = {
        'negotiation_rounds': max_negotiation_rounds,
        'unresolved_cities': len(unassigned_cities) if unassigned_cities else 0,
        'agent_distances': agent_distances,
        'load_fairness': load_fairness,
        'conflicts_resolved': len(conflicts) if 'conflicts' in locals() else 0,
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
        'additional_metrics': additional_metrics
    } 