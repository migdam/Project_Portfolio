"""Configuration management utilities."""

import os
from pathlib import Path
from typing import Any, Dict

import yaml


def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Dictionary containing configuration
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
    
    # Expand environment variables if present
    config = _expand_env_vars(config)
    
    return config


def _expand_env_vars(config: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively expand environment variables in config."""
    if isinstance(config, dict):
        return {k: _expand_env_vars(v) for k, v in config.items()}
    elif isinstance(config, list):
        return [_expand_env_vars(item) for item in config]
    elif isinstance(config, str) and config.startswith("${") and config.endswith("}"):
        env_var = config[2:-1]
        return os.getenv(env_var, config)
    return config


def get_model_config(model_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get configuration for a specific model.
    
    Args:
        model_name: Name of the model (prm, cop, slm, po)
        config: Full configuration dictionary
        
    Returns:
        Model-specific configuration
    """
    if model_name not in config.get("models", {}):
        raise ValueError(f"Model {model_name} not found in configuration")
    
    return config["models"][model_name]
