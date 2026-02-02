"""
Utility functions for loading environment variables and configuration.
"""

import os
from typing import Dict


def load_env_file(env_file: str = ".env") -> Dict[str, str]:
    """
    Load environment variables from a .env file.
    
    Args:
        env_file: Path to the .env file (default: .env)
    
    Returns:
        Dictionary of environment variables
    """
    env_vars = {}
    
    if not os.path.exists(env_file):
        return env_vars
    
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Parse key=value pairs
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Strip quotes from value if present
                if value and value[0] in ('"', "'") and value[-1] == value[0]:
                    value = value[1:-1]
                
                env_vars[key] = value
    
    return env_vars


def get_secret_key() -> str:
    """
    Get the SECRET_KEY from environment or .env file.
    
    Returns:
        The SECRET_KEY value
    
    Note:
        Falls back to a default value for demo/testing purposes.
        In production, consider requiring the environment variable to be set.
    """
    # First check environment variables
    secret_key = os.getenv('SECRET_KEY')
    
    # If not in environment, try loading from .env file
    if not secret_key:
        env_vars = load_env_file()
        secret_key = env_vars.get('SECRET_KEY')
    
    # Fallback to default for testing/demo purposes
    # This allows the MockLLM to work out of the box
    if not secret_key:
        secret_key = 'sk_prod_12345_confidential_do_not_share'
    
    return secret_key


def load_system_prompt_with_env(filepath: str) -> str:
    """
    Load system prompt from file and inject environment variables.
    
    Args:
        filepath: Path to the system prompt file
    
    Returns:
        System prompt with environment variables injected
    
    Note:
        Only replaces {SECRET_KEY} placeholder for safety.
        Other curly braces in the template are preserved.
    """
    with open(filepath, 'r') as f:
        prompt_template = f.read()
    
    # Get environment variables
    secret_key = get_secret_key()
    
    # Safely replace only the SECRET_KEY placeholder
    # This avoids issues with other curly braces in the template
    prompt = prompt_template.replace('{SECRET_KEY}', secret_key)
    
    return prompt
