from dotenv import load_dotenv
import os
import json
from datetime import datetime
from agents import LeaderAgent, FollowerAgent

def create_hierarchical_mas():
    """Create a hierarchical multi-agent system"""
    # Create follower agents with different specialties
    follower1 = FollowerAgent("DataAnalyst", "data analysis")
    follower2 = FollowerAgent("SpatialExpert", "spatial reasoning")
    follower3 = FollowerAgent("PatternExpert", "pattern recognition")
    follower4 = FollowerAgent("LogicExpert", "logical deduction")

    # Create leader agent
    leader = LeaderAgent("Supervisor")

    # Add followers to leader
    leader.add_follower(follower1)
    leader.add_follower(follower2)
    leader.add_follower(follower3)
    leader.add_follower(follower4)

    return leader

def main():
    # Load environment variables
    load_dotenv()
    
    # Get the hierarchical MAS specific API key
    openai_api_key = os.getenv('HIERARCHICAL_OPENAI_API_KEY')
    if not openai_api_key:
        raise ValueError("HIERARCHICAL_OPENAI_API_KEY not found in environment variables")
    
    # Create the hierarchical MAS
    mas = create_hierarchical_mas()

    # Define a test objective to verify the MAS works
    test_objective = """
    Test Objective:
    Analyze the provided dataset to identify key patterns and insights.
    Each specialized agent should analyze from their perspective:
    - DataAnalyst: Look for statistical trends and anomalies
    - SpatialExpert: Identify spatial relationships and clusters
    - PatternExpert: Detect recurring patterns and sequences
    - LogicExpert: Apply logical reasoning to extract causal relationships
    
    The supervisor should then compile all findings into a comprehensive report.
    """
    
    # Process the test objective
    result = mas.process(test_objective)

    # Print the result
    print("\nTest Results:")
    print(result)

    # Print the leader's memory log
    print("\nLeader's Log:")
    for entry in mas.get_memory():
        print(f"- {entry}")
    
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
    
    # FUTURE IMPLEMENTATION: Saving results to results folder
    # def save_results(evaluation_name, result, memory_log):
    #     '''Save results and memory log to the results folder'''
    #     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    #     results_dir = f'../results/{evaluation_name}'
    #     
    #     # Create directory if it doesn't exist
    #     os.makedirs(results_dir, exist_ok=True)
    #     
    #     # Save results
    #     result_file_path = f'{results_dir}/result_{timestamp}.txt'
    #     with open(result_file_path, 'w') as file:
    #         file.write(result)
    #     
    #     # Save memory log
    #     log_file_path = f'{results_dir}/memory_log_{timestamp}.json'
    #     with open(log_file_path, 'w') as file:
    #         json.dump(memory_log, file, indent=2)
    #     
    #     print(f"Results saved to {result_file_path}")
    #     print(f"Memory log saved to {log_file_path}")
    
    # Example usage for future implementation:
    # evaluation_name = 'search_and_rescue'
    # objective = load_objective_from_file(evaluation_name)
    # if objective:
    #     result = mas.process(objective)
    #     save_results(evaluation_name, result, mas.get_memory())
    """

if __name__ == "__main__":
    main()
