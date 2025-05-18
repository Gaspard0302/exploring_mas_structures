"""
Environment and Configuration Utilities

This module provides utilities for managing environment variables,
configuration, and other helper functions.
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any, Optional

def load_environment(env_file: str = '.env') -> Dict[str, str]:
    """Load environment variables from a .env file.
    
    Args:
        env_file: Path to the .env file
        
    Returns:
        Dictionary of loaded environment variables
    """
    # Load from .env file
    load_dotenv(env_file)
    
    # Collect environment variables relevant to our system
    mas_vars = {}
    for key, value in os.environ.items():
        if key.startswith(('OPENAI_', 'MAS_', 'HIERARCHICAL_', 'FLAT_', 'AUCTION_')):
            mas_vars[key] = value
    
    return mas_vars

def get_project_root() -> Path:
    """Get the absolute path to the project root directory.
    
    Returns:
        Path to the project root
    """
    # This assumes the script is in tools/utils
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent
    return project_root

def get_mas_config(mas_type: str) -> Dict[str, Any]:
    """Get configuration for a specific MAS type.
    
    Args:
        mas_type: Type of MAS (hierarchical, flat, auction)
        
    Returns:
        Configuration dictionary
    """
    config_path = get_project_root() / f"mas_{mas_type}" / "config.json"
    
    if not config_path.exists():
        # Return default configuration if file doesn't exist
        return {
            "name": f"{mas_type.capitalize()} MAS",
            "agent_count": 4,
            "debug": False,
            "log_level": "info"
        }
    
    with open(config_path, 'r') as file:
        return json.load(file)

def get_api_key(mas_type: str) -> Optional[str]:
    """Get the API key for a specific MAS type.
    
    Args:
        mas_type: Type of MAS (hierarchical, flat, auction)
        
    Returns:
        API key or None if not found
    """
    key_name = f"{mas_type.upper()}_OPENAI_API_KEY"
    return os.getenv(key_name)

def setup_directories() -> None:
    """Create necessary directories if they don't exist."""
    root = get_project_root()
    
    # Ensure these directories exist
    directories = [
        "evaluations",
        "results",
        "tools/mcp",
        "tools/utils"
    ]
    
    for directory in directories:
        dir_path = root / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        
    print("Directory structure verified.")

# Example usage
if __name__ == "__main__":
    # Load environment
    env_vars = load_environment()
    print(f"Loaded {len(env_vars)} environment variables")
    
    # Get project root
    root = get_project_root()
    print(f"Project root: {root}")
    
    # Get hierarchical MAS configuration
    config = get_mas_config("hierarchical")
    print(f"Hierarchical MAS config: {config}")
    
    # Get API key
    api_key = get_api_key("hierarchical")
    print(f"API key found: {bool(api_key)}")
    
    # Setup directories
    setup_directories() 