#!/usr/bin/env python3
"""
LLM-Powered Multi-Agent TSP Evaluation
Compares Hierarchical, Flat, and Auction-based MAS architectures using actual LLM agents
"""

import os
import json
import time
import argparse
from typing import Dict, Any, List, Tuple
from datetime import datetime

from .utils import TSPUtils
from .metrics import TSPEvaluator
from .llm_integration import get_logger, get_llm_integration
from .llm_hierarchical_tsp import evaluate_llm_hierarchical_tsp
from .llm_flat_tsp import evaluate_llm_flat_tsp
from .llm_auction_tsp import evaluate_llm_auction_tsp

def create_scenarios() -> List[Dict[str, Any]]:
    """Create different TSP scenarios for evaluation"""
    scenarios = [
        {
            "name": "Small_Clustered",
            "n_cities": 8,
            "n_agents": 3,
            "seed": 42,
            "description": "Small clustered cities with clear geographical separation"
        },
        {
            "name": "Medium_Mixed",
            "n_cities": 12,
            "n_agents": 4,
            "seed": 123,
            "description": "Medium-sized problem with mixed clustering patterns"
        },
        {
            "name": "Medium_Random",
            "n_cities": 15,
            "n_agents": 4,
            "seed": 456,
            "description": "Medium random distribution testing adaptability"
        }
    ]
    return scenarios

def run_llm_evaluation(api_key: str, save_results: bool = True) -> Dict[str, Any]:
    """
    Run comprehensive LLM-powered MAS TSP evaluation
    
    Args:
        api_key: OpenAI API key
        save_results: Whether to save detailed results to files
    
    Returns:
        Complete evaluation results with LLM logs and analysis
    """
    
    print("🤖 Starting LLM-Powered Multi-Agent TSP Evaluation")
    print("=" * 60)
    
    # Initialize tracking
    start_time = time.time()
    scenarios = create_scenarios()
    results = {
        "evaluation_metadata": {
            "timestamp": datetime.now().isoformat(),
            "scenarios": scenarios,
            "architectures": ["hierarchical", "flat", "auction"],
            "total_runs": len(scenarios) * 3
        },
        "scenario_results": {},
        "architecture_comparison": {},
        "llm_analysis": {},
        "detailed_logs": {}
    }
    
    # Test API connection
    try:
        llm = get_llm_integration(api_key)
        test_response = llm.call_llm(
            agent_name="System",
            agent_type="system",
            call_type="connection_test",
            prompt="Test connection. Respond with 'OK'.",
            context={"test": True}
        )
        print(f"✅ LLM Connection Test: {test_response.strip()}")
    except Exception as e:
        print(f"❌ LLM Connection Failed: {e}")
        return {"error": "LLM connection failed", "details": str(e)}
    
    print()
    
    # Run evaluations for each scenario
    for scenario_idx, scenario in enumerate(scenarios):
        scenario_name = scenario["name"]
        print(f"📍 Scenario {scenario_idx + 1}/{len(scenarios)}: {scenario_name}")
        print(f"   {scenario['description']}")
        print(f"   Cities: {scenario['n_cities']}, Agents: {scenario['n_agents']}")
        
        # Generate cities for this scenario
        cities = TSPUtils.generate_cities(scenario["n_cities"], seed=scenario["seed"])
        scenario_results = {
            "scenario_info": scenario,
            "cities": cities,
            "architecture_results": {}
        }
        
        # Evaluate each architecture
        architectures = [
            ("hierarchical", evaluate_llm_hierarchical_tsp),
            ("flat", evaluate_llm_flat_tsp),
            ("auction", evaluate_llm_auction_tsp)
        ]
        
        for arch_name, eval_func in architectures:
            print(f"   🏗️  Running {arch_name.title()} MAS...")
            
            try:
                # Reset logger for this run
                logger = get_logger()
                logger.llm_calls.clear()
                logger.communications.clear()
                
                # Run evaluation
                arch_start_time = time.time()
                result = eval_func(
                    cities=cities,
                    n_agents=scenario["n_agents"],
                    api_key=api_key,
                    seed=scenario["seed"]
                )
                arch_duration = time.time() - arch_start_time
                
                # Add timing and log info
                result['evaluation_duration'] = arch_duration
                result['llm_logs'] = {
                    "session_summary": logger.get_session_summary(),
                    "total_calls": len(logger.llm_calls),
                    "total_communications": len(logger.communications)
                }
                
                scenario_results["architecture_results"][arch_name] = result
                
                # Print quick summary
                total_dist = result['total_distance']
                comm_overhead = result['communication_overhead']
                llm_calls = result['additional_metrics'].get('llm_calls', 0)
                llm_cost = result['additional_metrics'].get('total_llm_cost', 0)
                
                print(f"      ✅ Distance: {total_dist:.2f}, "
                      f"Comm: {comm_overhead}, "
                      f"LLM Calls: {llm_calls}, "
                      f"Cost: ${llm_cost:.3f}, "
                      f"Time: {arch_duration:.1f}s")
                
                # Save detailed logs if requested
                if save_results:
                    log_files = logger.save_logs()
                    result['log_files'] = log_files
                
            except Exception as e:
                print(f"      ❌ Error in {arch_name}: {e}")
                scenario_results["architecture_results"][arch_name] = {
                    "error": str(e),
                    "total_distance": float('inf'),
                    "communication_overhead": 0,
                    "evaluation_duration": 0
                }
        
        results["scenario_results"][scenario_name] = scenario_results
        print()
    
    # Comparative Analysis
    print("📊 Performing Comparative Analysis...")
    
    # Aggregate results across scenarios
    architecture_stats = {
        "hierarchical": {"distances": [], "times": [], "communications": [], "llm_costs": []},
        "flat": {"distances": [], "times": [], "communications": [], "llm_costs": []},
        "auction": {"distances": [], "times": [], "communications": [], "llm_costs": []}
    }
    
    for scenario_name, scenario_data in results["scenario_results"].items():
        for arch_name, arch_result in scenario_data["architecture_results"].items():
            if "error" not in arch_result:
                stats = architecture_stats[arch_name]
                stats["distances"].append(arch_result["total_distance"])
                stats["times"].append(arch_result["evaluation_duration"])
                stats["communications"].append(arch_result["communication_overhead"])
                stats["llm_costs"].append(arch_result["additional_metrics"].get("total_llm_cost", 0))
    
    # Calculate comparative metrics
    comparison = {}
    for arch_name, stats in architecture_stats.items():
        if stats["distances"]:
            comparison[arch_name] = {
                "avg_distance": sum(stats["distances"]) / len(stats["distances"]),
                "avg_time": sum(stats["times"]) / len(stats["times"]),
                "avg_communications": sum(stats["communications"]) / len(stats["communications"]),
                "avg_llm_cost": sum(stats["llm_costs"]) / len(stats["llm_costs"]),
                "total_scenarios": len(stats["distances"]),
                "distance_std": (sum((d - sum(stats["distances"]) / len(stats["distances"]))**2 for d in stats["distances"]) / len(stats["distances"]))**0.5 if len(stats["distances"]) > 1 else 0
            }
    
    results["architecture_comparison"] = comparison
    
    # LLM-powered analysis of results
    print("🧠 Generating LLM Analysis of Results...")
    
    analysis_prompt = f"""
You are an AI researcher analyzing multi-agent system architectures for collaborative problem solving.

EVALUATION RESULTS:
{json.dumps(comparison, indent=2)}

RESEARCH CONTEXT:
This evaluation compared three MAS architectures using LLM agents solving TSP collaboratively:

1. HIERARCHICAL: Leader coordinates followers, top-down decision making
2. FLAT: Peer-to-peer negotiation, distributed decision making  
3. AUCTION: Competitive bidding with auctioneer mediation

KEY QUESTIONS TO ANALYZE:
1. Which architecture produces the most efficient solutions (lowest travel distance)?
2. How do communication patterns differ between architectures?
3. What are the computational costs (LLM calls/costs) of each approach?
4. Which architecture demonstrates the best collaborative reasoning?
5. How might these findings relate to human organizational behavior?

ANALYSIS FRAMEWORK:
- Solution Quality: Average distances and consistency
- Efficiency: Computation time and communication overhead
- Scalability: LLM usage and cost implications
- Collaboration Patterns: Communication types and effectiveness
- Human Parallels: How do these results mirror human group dynamics?

Provide a comprehensive analysis addressing these questions and draw insights about:
- Optimal conditions for each architecture
- Trade-offs between solution quality and coordination costs
- Implications for AI agent organization design
- Parallels to human organizational psychology

Format your response as structured analysis with clear sections and actionable insights.
"""
    
    try:
        analysis_response = llm.call_llm(
            agent_name="Meta_Analyst",
            agent_type="analyst",
            call_type="comprehensive_analysis", 
            prompt=analysis_prompt,
            context={"results": comparison, "scenarios": len(scenarios)}
        )
        results["llm_analysis"]["comprehensive_analysis"] = analysis_response
    except Exception as e:
        results["llm_analysis"]["error"] = f"Analysis generation failed: {e}"
    
    # Final timing
    total_duration = time.time() - start_time
    results["evaluation_metadata"]["total_duration"] = total_duration
    
    # Save results if requested
    if save_results:
        results_dir = "results/llm_tsp"
        os.makedirs(results_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = os.path.join(results_dir, f"llm_evaluation_{timestamp}.json")
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        results["saved_file"] = results_file
        print(f"💾 Results saved to: {results_file}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("📋 EVALUATION SUMMARY")
    print("=" * 60)
    
    if comparison:
        print("\n🏆 Performance Rankings (Average Distance):")
        sorted_archs = sorted(comparison.items(), key=lambda x: x[1]["avg_distance"])
        for i, (arch, stats) in enumerate(sorted_archs):
            print(f"   {i+1}. {arch.title()}: {stats['avg_distance']:.2f} "
                  f"(±{stats['distance_std']:.2f})")
        
        print(f"\n💰 Cost Analysis:")
        for arch, stats in comparison.items():
            print(f"   {arch.title()}: ${stats['avg_llm_cost']:.3f} per scenario, "
                  f"{stats['avg_communications']:.1f} messages")
        
        print(f"\n⏱️  Time Analysis:")
        for arch, stats in comparison.items():
            print(f"   {arch.title()}: {stats['avg_time']:.1f}s per scenario")
    
    print(f"\n📊 Total Evaluation Time: {total_duration:.1f}s")
    print(f"🎯 Scenarios Completed: {len(scenarios)}")
    print(f"🤖 Architectures Tested: 3")
    
    return results

def main():
    """Main entry point for LLM TSP evaluation"""
    parser = argparse.ArgumentParser(description="LLM-Powered Multi-Agent TSP Evaluation")
    parser.add_argument("--api-key", type=str, help="OpenAI API key (or set OPENAI_API_KEY env var or config.py)")
    parser.add_argument("--no-save", action="store_true", help="Don't save detailed results to files")
    parser.add_argument("--quick", action="store_true", help="Run only small scenario for quick testing")
    
    args = parser.parse_args()
    
    # Get API key from multiple sources
    api_key = None
    try:
        if args.api_key:
            api_key = args.api_key
        else:
            # Try to get from config or environment
            try:
                from config import get_openai_api_key
                api_key = get_openai_api_key()
            except ImportError:
                # Fallback to environment variable
                api_key = os.getenv('OPENAI_API_KEY')
                if not api_key:
                    raise ValueError("No API key found")
    except Exception as e:
        print("❌ Error: OpenAI API key required.")
        print("Please either:")
        print("1. Copy config_template.py to config.py and set your API key")
        print("2. Set OPENAI_API_KEY environment variable")
        print("3. Use --api-key argument")
        return
    
    # Modify scenarios if quick test
    if args.quick:
        global create_scenarios
        original_create_scenarios = create_scenarios
        def create_scenarios():
            scenarios = original_create_scenarios()
            return [scenarios[0]]  # Only first scenario
        print("🚀 Quick test mode: Running only first scenario")
    
    # Run evaluation
    try:
        results = run_llm_evaluation(api_key, save_results=not args.no_save)
        
        if "error" not in results:
            print("\n✅ Evaluation completed successfully!")
            
            # Print key insights if available
            if "llm_analysis" in results and "comprehensive_analysis" in results["llm_analysis"]:
                print("\n🧠 Key Insights:")
                analysis = results["llm_analysis"]["comprehensive_analysis"]
                # Print first few lines of analysis
                lines = analysis.split('\n')[:5]
                for line in lines:
                    if line.strip():
                        print(f"   {line.strip()}")
                print("   ... (see full results for complete analysis)")
        else:
            print(f"❌ Evaluation failed: {results['error']}")
            
    except KeyboardInterrupt:
        print("\n⏹️  Evaluation interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main() 