from typing import List, Tuple, Dict, Any
import json
import random
from .utils import TSPUtils
from .llm_integration import get_llm_integration, get_logger

def evaluate_llm_auction_tsp(cities: List[Tuple[int, int]], n_agents: int, 
                            api_key: str, seed: int = 42) -> Dict[str, Any]:
    """
    Evaluate Auction-based MAS with LLM agents using strategic bidding on TSP
    
    Args:
        cities: List of city coordinates
        n_agents: Number of bidder agents
        api_key: OpenAI API key
        seed: Random seed for reproducibility
    
    Returns:
        Dictionary with evaluation results and LLM logs
    """
    
    random.seed(seed)
    llm = get_llm_integration(api_key)
    logger = get_logger()
    
    # Initialize bidder agents with different strategies and starting budgets
    agent_data = {}
    strategies = [
        "Conservative Bidder", "Aggressive Bidder", "Strategic Bidder", 
        "Efficiency Optimizer", "Risk Taker", "Analytical Bidder"
    ][:n_agents]
    
    for i in range(n_agents):
        agent_name = f"Bidder_{i}"
        agent_data[agent_name] = {
            "strategy": strategies[i],
            "budget": 1000,
            "assigned_cities": [],
            "route": [],
            "total_distance": 0,
            "reasoning_history": []
        }
    
    # Step 1: Auctioneer introduces the auction and agents analyze
    auctioneer_intro = f"""
You are the AUCTIONEER for a TSP city auction with {n_agents} bidder agents.

AUCTION OVERVIEW:
- Cities to auction: {cities} (total: {len(cities)})
- Bidders: {n_agents} agents with $1000 budgets each
- Goal: Each bidder will plan an optimal route through their won cities
- Auction format: Sequential city auctions

YOUR ROLE:
1. Conduct fair auctions for each city
2. Evaluate bids considering strategic merit, not just amount
3. Ensure competitive but fair distribution

Begin by analyzing the cities and setting auction expectations.

What are your observations about:
1. The city layout and clustering patterns
2. Expected bidding strategies
3. How to ensure fair competition
"""
    
    auctioneer_analysis = llm.call_llm(
        agent_name="Auctioneer",
        agent_type="auctioneer",
        call_type="auction_setup",
        prompt=auctioneer_intro,
        context={"cities": cities, "n_agents": n_agents}
    )
    
    # Log auctioneer's introduction
    llm.log_communication(
        sender="Auctioneer",
        receiver="All_Bidders",
        message_type="auction_introduction",
        content=f"Auction starting. Analysis: {auctioneer_analysis}",
        context={"cities": cities, "setup": auctioneer_analysis}
    )
    
    # Step 2: Agents analyze their strategies
    for agent_name, data in agent_data.items():
        strategy = data["strategy"]
        
        strategy_prompt = f"""
You are {agent_name}, a {strategy} participating in a TSP city auction.

AUCTION CONTEXT:
- Cities being auctioned: {cities}
- Your budget: ${data["budget"]}
- Other bidders: {n_agents - 1} competitors with similar budgets
- Your bidding personality: {strategy}

STRATEGIC ANALYSIS:
Based on your {strategy} approach, analyze:
1. Which cities look most valuable for building efficient routes?
2. What's your overall bidding strategy across all auctions?
3. How will you balance aggressive vs. conservative bidding?
4. What geographic patterns do you see that align with your strategy?

Format your response as JSON:
{{
    "strategy_overview": "your overall approach to the auction",
    "target_cities": [list_of_city_indices_you_most_want],
    "bidding_philosophy": "how you'll approach individual auctions",
    "budget_allocation": "how you plan to manage your $1000 budget"
}}
"""
        
        strategy_response = llm.call_llm(
            agent_name=agent_name,
            agent_type="bidder",
            call_type="strategy_planning",
            prompt=strategy_prompt,
            context={"strategy": strategy, "budget": data["budget"], "cities": cities}
        )
        
        # Parse strategy
        try:
            strategy_data = json.loads(strategy_response)
            data["strategy_overview"] = strategy_data.get("strategy_overview", "No strategy provided")
            data["target_cities"] = strategy_data.get("target_cities", [])
            data["bidding_philosophy"] = strategy_data.get("bidding_philosophy", "No philosophy provided")
        except json.JSONDecodeError:
            data["strategy_overview"] = "Parsing error in strategy"
            data["target_cities"] = []
            data["bidding_philosophy"] = "Default bidding approach"
        
        # Log strategy
        llm.log_communication(
            sender=agent_name,
            receiver="Auctioneer",
            message_type="strategy_declaration",
            content=f"Strategy: {data['strategy_overview']}",
            context={"strategy": strategy, "targets": data["target_cities"]}
        )
    
    # Step 3: Conduct auctions for each city
    auction_results = []
    
    for city_idx, city_coords in enumerate(cities):
        # Each agent decides their bid using LLM reasoning
        bids = {}
        
        for agent_name, data in agent_data.items():
            if data["budget"] <= 0:
                continue  # Skip if no budget left
            
            current_cities = data["assigned_cities"]
            current_coords = [cities[i] for i in current_cities]
            
            bidding_prompt = f"""
You are {agent_name} ({data["strategy"]}) bidding on City {city_idx} at coordinates {city_coords}.

CURRENT SITUATION:
- Your budget remaining: ${data["budget"]}
- Your current cities: {current_cities}
- Current city coordinates: {current_coords}
- Auction item: City {city_idx} at {city_coords}

BIDDING DECISION:
Consider your {data["strategy"]} approach:
1. How valuable is this city for your route optimization?
2. How does it fit with your current city collection?
3. What's the maximum you should bid given your budget and strategy?
4. How aggressive should you be based on your remaining budget?

Your strategic context:
- Strategy overview: {data["strategy_overview"]}
- Bidding philosophy: {data["bidding_philosophy"]}
- Target cities: {data["target_cities"]}

Calculate your bid and provide reasoning.

Format as JSON:
{{
    "bid_amount": your_numeric_bid_amount,
    "reasoning": "detailed explanation for your bid",
    "confidence": "how confident you are in this bid (high/medium/low)",
    "strategic_importance": "how important this city is to your overall strategy"
}}
"""
            
            bid_response = llm.call_llm(
                agent_name=agent_name,
                agent_type="bidder",
                call_type="bidding_decision",
                prompt=bidding_prompt,
                context={
                    "city": city_idx,
                    "coordinates": city_coords,
                    "budget": data["budget"],
                    "current_cities": current_cities,
                    "strategy": data["strategy"]
                }
            )
            
            # Parse bid
            try:
                bid_data = json.loads(bid_response)
                bid_amount = float(bid_data.get("bid_amount", 0))
                reasoning = bid_data.get("reasoning", "No reasoning provided")
                confidence = bid_data.get("confidence", "medium")
                strategic_importance = bid_data.get("strategic_importance", "unknown")
            except (json.JSONDecodeError, ValueError):
                bid_amount = 0
                reasoning = "Parsing error in bid"
                confidence = "low"
                strategic_importance = "unknown"
            
            # Ensure bid doesn't exceed budget
            bid_amount = min(bid_amount, data["budget"])
            
            if bid_amount > 0:
                bids[agent_name] = {
                    "amount": bid_amount,
                    "reasoning": reasoning,
                    "confidence": confidence,
                    "strategic_importance": strategic_importance
                }
                
                # Log the bid
                llm.log_communication(
                    sender=agent_name,
                    receiver="Auctioneer",
                    message_type="bid_submission",
                    content=f"Bidding ${bid_amount:.2f} for City {city_idx}. Reasoning: {reasoning}",
                    context={
                        "city": city_idx,
                        "bid": bid_amount,
                        "reasoning": reasoning,
                        "confidence": confidence
                    }
                )
        
        # Auctioneer evaluates bids using LLM judgment
        if not bids:
            # No bids received
            auction_result = {
                "city": city_idx,
                "winner": None,
                "winning_bid": 0,
                "total_bids": 0,
                "reasoning": "No bids received"
            }
        else:
            # Auctioneer makes decision
            auctioneer_prompt = f"""
You are the AUCTIONEER evaluating bids for City {city_idx} at coordinates {city_coords}.

RECEIVED BIDS:
"""
            for bidder, bid_info in bids.items():
                auctioneer_prompt += f"- {bidder}: ${bid_info['amount']:.2f}\n"
                auctioneer_prompt += f"  Reasoning: {bid_info['reasoning']}\n"
                auctioneer_prompt += f"  Confidence: {bid_info['confidence']}\n"
                auctioneer_prompt += f"  Strategic importance: {bid_info['strategic_importance']}\n\n"
            
            auctioneer_prompt += f"""
EVALUATION CRITERIA:
While highest bid usually wins, consider:
1. Strategic merit of each bid's reasoning
2. Confidence levels and planning quality
3. Fairness in distribution (current agent holdings)
4. Quality of strategic thinking demonstrated

Current holdings:"""
            for agent_name, data in agent_data.items():
                auctioneer_prompt += f"\n- {agent_name}: {len(data['assigned_cities'])} cities"
            
            auctioneer_prompt += f"""

Determine the winner and provide your reasoning for the decision.

Format as JSON:
{{
    "winner": "winning_agent_name",
    "winning_bid": winning_bid_amount,
    "reasoning": "your detailed reasoning for the choice",
    "fairness_consideration": "how you balanced fairness vs. bid amounts"
}}
"""
            
            auctioneer_decision = llm.call_llm(
                agent_name="Auctioneer",
                agent_type="auctioneer",
                call_type="bid_evaluation",
                prompt=auctioneer_prompt,
                context={
                    "city": city_idx,
                    "bids": bids,
                    "current_holdings": {name: len(data["assigned_cities"]) for name, data in agent_data.items()}
                }
            )
            
            # Parse auctioneer decision
            try:
                decision_data = json.loads(auctioneer_decision)
                winner = decision_data.get("winner", max(bids.keys(), key=lambda k: bids[k]["amount"]))
                winning_bid = decision_data.get("winning_bid", bids[winner]["amount"])
                auctioneer_reasoning = decision_data.get("reasoning", "Highest bidder wins")
            except (json.JSONDecodeError, KeyError):
                # Fallback to highest bidder
                winner = max(bids.keys(), key=lambda k: bids[k]["amount"])
                winning_bid = bids[winner]["amount"]
                auctioneer_reasoning = "Fallback to highest bidder"
            
            # Validate winner
            if winner not in bids:
                winner = max(bids.keys(), key=lambda k: bids[k]["amount"])
                winning_bid = bids[winner]["amount"]
            
            auction_result = {
                "city": city_idx,
                "winner": winner,
                "winning_bid": winning_bid,
                "total_bids": len(bids),
                "reasoning": auctioneer_reasoning,
                "all_bids": {k: v["amount"] for k, v in bids.items()}
            }
            
            # Update winner's data
            agent_data[winner]["assigned_cities"].append(city_idx)
            agent_data[winner]["budget"] -= winning_bid
        
        auction_results.append(auction_result)
        
        # Log auction result
        if auction_result["winner"]:
            llm.log_communication(
                sender="Auctioneer",
                receiver="All_Bidders",
                message_type="auction_result",
                content=f"City {city_idx} won by {auction_result['winner']} for ${auction_result['winning_bid']:.2f}. {auctioneer_reasoning}",
                context=auction_result
            )
    
    # Step 4: Each agent optimizes their final route
    total_distance = 0
    agent_loads = []
    agent_routes = {}
    agent_distances = {}
    
    for agent_name, data in agent_data.items():
        city_indices = data["assigned_cities"]
        agent_loads.append(len(city_indices))
        
        if not city_indices:
            agent_routes[agent_name] = []
            agent_distances[agent_name] = 0
            continue
        
        agent_cities = [cities[i] for i in city_indices]
        
        # Final route optimization with LLM
        route_prompt = f"""
You are {agent_name} optimizing your final route through your won cities.

FINAL RESULTS:
- Cities won: {city_indices}
- Coordinates: {agent_cities}
- Money spent: ${1000 - data["budget"]:.2f}
- Remaining budget: ${data["budget"]:.2f}

ROUTE OPTIMIZATION:
Plan the most efficient route through your cities to minimize total travel distance.

Analyze different route possibilities and provide your optimal solution.

Format as JSON:
{{
    "route_analysis": "your analysis of different route options",
    "optimal_route": [ordered_list_of_city_indices],
    "estimated_distance": your_estimated_total_distance,
    "auction_reflection": "reflection on your auction performance and strategy effectiveness"
}}
"""
        
        route_response = llm.call_llm(
            agent_name=agent_name,
            agent_type="bidder",
            call_type="final_route_optimization",
            prompt=route_prompt,
            context={
                "won_cities": city_indices,
                "coordinates": agent_cities,
                "money_spent": 1000 - data["budget"]
            }
        )
        
        # Parse final route
        try:
            route_data = json.loads(route_response)
            planned_route = route_data.get("optimal_route", city_indices)
            route_analysis = route_data.get("route_analysis", "No analysis provided")
            auction_reflection = route_data.get("auction_reflection", "No reflection provided")
        except json.JSONDecodeError:
            planned_route = city_indices
            route_analysis = "Parsing error in route"
            auction_reflection = "Unable to parse reflection"
        
        # Calculate actual distance
        if len(agent_cities) <= 1:
            actual_distance = 0
        else:
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
        
        data["route"] = planned_route
        data["total_distance"] = actual_distance
        data["reasoning_history"].append({
            "type": "final_optimization",
            "analysis": route_analysis,
            "reflection": auction_reflection
        })
        
        # Log final result
        llm.log_communication(
            sender=agent_name,
            receiver="Auctioneer",
            message_type="final_submission",
            content=f"Final route: {planned_route}, Distance: {actual_distance:.2f}. Reflection: {auction_reflection}",
            context={"route": planned_route, "distance": actual_distance, "budget_used": 1000 - data["budget"]}
        )
    
    # Calculate metrics
    communication_overhead = len(logger.communications)
    total_revenue = sum(result["winning_bid"] for result in auction_results if result["winner"])
    avg_bid = total_revenue / len(cities) if cities else 0
    
    # Calculate money fairness
    money_spent = [1000 - data["budget"] for data in agent_data.values()]
    mean_spent = sum(money_spent) / len(money_spent) if money_spent else 0
    money_variance = sum((spent - mean_spent) ** 2 for spent in money_spent) / len(money_spent) if money_spent else 0
    money_fairness = (money_variance ** 0.5) / mean_spent if mean_spent > 0 else 0
    
    additional_metrics = {
        'total_auction_revenue': total_revenue,
        'average_bid': avg_bid,
        'avg_bidders_per_auction': sum(result["total_bids"] for result in auction_results) / len(auction_results) if auction_results else 0,
        'money_fairness': money_fairness,
        'agent_distances': agent_distances,
        'auction_results': auction_results[:10],  # Store first 10 for analysis
        'final_budgets': {name: data["budget"] for name, data in agent_data.items()},
        'llm_calls': len(logger.llm_calls),
        'total_tokens': sum(call.tokens_used or 0 for call in logger.llm_calls),
        'total_llm_cost': sum(call.cost or 0 for call in logger.llm_calls),
        'agent_strategies': {name: data["strategy"] for name, data in agent_data.items()}
    }
    
    return {
        'total_distance': total_distance,
        'communication_overhead': communication_overhead,
        'agent_loads': agent_loads,
        'agent_routes': agent_routes,
        'additional_metrics': additional_metrics
    } 