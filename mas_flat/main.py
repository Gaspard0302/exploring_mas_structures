from dotenv import load_dotenv
import os
import json
from datetime import datetime
from agents import PeerAgent

def create_flat_mas():
    """Create a flat multi-agent system with peer-to-peer communication"""
    # Create agents with different specialties
    data_analyst = PeerAgent("DataAnalyst", "data analysis")
    spatial_expert = PeerAgent("SpatialExpert", "spatial reasoning")
    pattern_expert = PeerAgent("PatternExpert", "pattern recognition")
    logic_expert = PeerAgent("LogicExpert", "logical deduction")
    
    # Connect agents in a peer network (full mesh)
    data_analyst.add_peer(spatial_expert)
    data_analyst.add_peer(pattern_expert)
    data_analyst.add_peer(logic_expert)
    
    spatial_expert.add_peer(data_analyst)
    spatial_expert.add_peer(pattern_expert)
    spatial_expert.add_peer(logic_expert)
    
    pattern_expert.add_peer(data_analyst)
    pattern_expert.add_peer(spatial_expert)
    pattern_expert.add_peer(logic_expert)
    
    logic_expert.add_peer(data_analyst)
    logic_expert.add_peer(spatial_expert)
    logic_expert.add_peer(pattern_expert)
    
    # Return the network of agents
    agents = {
        "DataAnalyst": data_analyst,
        "SpatialExpert": spatial_expert,
        "PatternExpert": pattern_expert,
        "LogicExpert": logic_expert
    }
    
    return agents

def main():
    # Load environment variables
    load_dotenv()
    
    # Get the flat MAS specific API key
    openai_api_key = os.getenv('FLAT_OPENAI_API_KEY')
    if not openai_api_key:
        raise ValueError("FLAT_OPENAI_API_KEY not found in environment variables")
    
    # Create the flat MAS
    agents = create_flat_mas()
    
    # Define a test objective to verify the MAS works
    test_objective = """
    Test Objective:
    Analyze the provided dataset to identify key patterns and insights.
    Each specialized agent should analyze from their perspective:
    - DataAnalyst: Look for statistical trends and anomalies
    - SpatialExpert: Identify spatial relationships and clusters
    - PatternExpert: Detect recurring patterns and sequences
    - LogicExpert: Apply logical reasoning to extract causal relationships
    
    Then collaborate to compile all findings into a comprehensive report.
    """
    
    # Distribute the test objective to all agents
    print("\nDistributing the test objective to all agents...")
    for name, agent in agents.items():
        print(f"Sending objective to {name}")
        agent.update_context("objective", test_objective)
    
    # Each agent processes the objective individually
    print("\nIndividual processing results:")
    individual_results = {}
    for name, agent in agents.items():
        task = f"Analyze data from {name} perspective"
        result = agent.process(task)
        individual_results[name] = result
        print(f"- {name}: {result}")
    
    # Initiate collaboration (select one agent to coordinate)
    print("\nInitiating collaboration...")
    collaboration_result = agents["DataAnalyst"].collaborate(
        "Compile comprehensive analysis by combining individual insights",
        required_specialties=["spatial reasoning", "pattern recognition", "logical deduction"]
    )
    
    # Print the collaboration result
    print("\nCollaboration Results:")
    print(collaboration_result)
    
    # Share knowledge between agents
    print("\nSharing knowledge between agents...")
    for name, agent in agents.items():
        shares = agent.share_knowledge()
        print(f"- {name} shared knowledge with {shares} peers")
    
    # Print message logs from one agent
    print("\nMessage log from DataAnalyst:")
    for message in agents["DataAnalyst"].get_memory():
        print(f"- {message}")
    
    """
    # FUTURE IMPLEMENTATION: Loading objectives from evaluations folder
    # def load_objective_from_file(evaluation_name):
    #     '''Load an objective from the evaluations folder'''
    #     eval_file_path = f'../evaluations/{evaluation_name}/objective.json'
    #     try:
    #         with open(eval_file_path, 'r') as file:
    #             data = json.load(file)
    #             return data.get('objective', 'No objective found')
    #     except FileNotFoundError:
    #         print(f"Evaluation file not found: {eval_file_path}")
    #         return None
    #     except json.JSONDecodeError:
    #         print(f"Invalid JSON in evaluation file: {eval_file_path}")
    #         return None
    
    # FUTURE IMPLEMENTATION: Running experiments with all agents
    # def run_experiment(evaluation_name, agents):
    #     '''Run a specific experiment with all agents in the flat MAS'''
    #     print(f"Running experiment: {evaluation_name}")
    #     
    #     # Load objective from evaluation
    #     objective = load_objective_from_file(evaluation_name)
    #     if not objective:
    #         return "Failed to load experiment objective"
    #     
    #     # Distribute objective to all agents
    #     for name, agent in agents.items():
    #         agent.update_context("objective", objective)
    #         agent.update_context("evaluation", evaluation_name)
    #     
    #     # Define tasks specific to each experiment type
    #     experiment_tasks = {
    #         "search_and_rescue": {
    #             "DataAnalyst": "Analyze victim location data",
    #             "SpatialExpert": "Map optimal rescue routes",
    #             "PatternExpert": "Identify patterns in victim distributions",
    #             "LogicExpert": "Prioritize rescue operations"
    #         },
    #         "foraging": {
    #             "DataAnalyst": "Analyze resource distribution data",
    #             "SpatialExpert": "Map efficient collection routes",
    #             "PatternExpert": "Identify resource regeneration patterns",
    #             "LogicExpert": "Optimize collection strategy"
    #         },
    #         "warehouse_fulfillment": {
    #             "DataAnalyst": "Analyze order frequency and patterns",
    #             "SpatialExpert": "Map optimal warehouse routes",
    #             "PatternExpert": "Identify product grouping patterns",
    #             "LogicExpert": "Optimize order fulfillment strategy"
    #         }
    #     }
    #     
    #     if evaluation_name not in experiment_tasks:
    #         tasks = {name: f"Process {evaluation_name} objective" for name in agents.keys()}
    #     else:
    #         tasks = experiment_tasks[evaluation_name]
    #     
    #     # Individual processing
    #     individual_results = {}
    #     for name, agent in agents.items():
    #         if name in tasks:
    #             task = tasks[name]
    #             result = agent.process(task)
    #             individual_results[name] = result
    #     
    #     # Collaboration
    #     coordinator = next(iter(agents.values()))  # Pick first agent as coordinator
    #     collaboration_result = coordinator.collaborate(
    #         f"Collaborate on {evaluation_name} objective", 
    #         required_specialties=None  # Use all available specialties
    #     )
    #     
    #     # Save results
    #     save_results(evaluation_name, individual_results, collaboration_result, agents)
    #     
    #     return collaboration_result
    
    # FUTURE IMPLEMENTATION: Saving results to results folder
    # def save_results(evaluation_name, individual_results, collaboration_result, agents):
    #     '''Save results to the results folder'''
    #     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    #     results_dir = f'../results/{evaluation_name}'
    #     
    #     # Create directory if it doesn't exist
    #     os.makedirs(results_dir, exist_ok=True)
    #     
    #     # Save individual results
    #     indiv_file_path = f'{results_dir}/individual_results_{timestamp}.json'
    #     with open(indiv_file_path, 'w') as file:
    #         json.dump(individual_results, file, indent=2)
    #     
    #     # Save collaboration result
    #     collab_file_path = f'{results_dir}/collaboration_result_{timestamp}.txt'
    #     with open(collab_file_path, 'w') as file:
    #         file.write(collaboration_result)
    #     
    #     # Save agent memory logs
    #     for name, agent in agents.items():
    #         log_file_path = f'{results_dir}/{name}_log_{timestamp}.json'
    #         with open(log_file_path, 'w') as file:
    #             json.dump(agent.get_memory(), file, indent=2)
    #     
    #     # Save network information
    #     network_info = {name: agent.get_network_info() for name, agent in agents.items()}
    #     network_file_path = f'{results_dir}/network_info_{timestamp}.json'
    #     with open(network_file_path, 'w') as file:
    #         json.dump(network_info, file, indent=2)
    #     
    #     print(f"Results saved to {results_dir}")
    
    # Example usage for future implementation:
    # evaluation_name = 'search_and_rescue'
    # agents = create_flat_mas()
    # final_result = run_experiment(evaluation_name, agents)
    """

if __name__ == "__main__":
    main()
