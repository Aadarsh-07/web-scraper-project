import yaml
import os
from typing import Dict, Any

def load_config() -> Dict[str, Any]:
    """Load configuration from YAML file"""
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'settings.yaml')
    
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    return config

def get_role_mappings() -> Dict[str, Any]:
    """Load role mappings from JSON file"""
    import json
    
    mapping_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'roles_mapping.json')
    
    with open(mapping_path, 'r') as file:
        mappings = json.load(file)
    
    return mappings
