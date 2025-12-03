"""Model registry for tracking versions."""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

from utils.logger import setup_logger

logger = setup_logger(__name__)


class ModelRegistry:
    """Track model versions and metadata."""
    
    def __init__(self, registry_path: str = "models/registry.json"):
        """Initialize model registry."""
        self.registry_path = Path(registry_path)
        self.registry = self._load_registry()
    
    def _load_registry(self) -> Dict:
        """Load registry from file."""
        if self.registry_path.exists():
            with open(self.registry_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_registry(self):
        """Save registry to file."""
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.registry_path, 'w') as f:
            json.dump(self.registry, f, indent=2)
    
    def register_model(
        self,
        model_name: str,
        version: str,
        metrics: Dict[str, float],
        artifacts_path: str,
        metadata: Dict = None
    ):
        """Register a new model version."""
        if model_name not in self.registry:
            self.registry[model_name] = {"versions": []}
        
        version_record = {
            "version": version,
            "registered_at": datetime.now().isoformat(),
            "metrics": metrics,
            "artifacts_path": artifacts_path,
            "metadata": metadata or {},
            "status": "active"
        }
        
        self.registry[model_name]["versions"].append(version_record)
        self.registry[model_name]["latest_version"] = version
        self._save_registry()
        
        logger.info(f"Registered {model_name} version {version}")
    
    def get_model_versions(self, model_name: str) -> List[Dict]:
        """Get all versions of a model."""
        return self.registry.get(model_name, {}).get("versions", [])
    
    def get_latest_version(self, model_name: str) -> Dict:
        """Get latest version of a model."""
        versions = self.get_model_versions(model_name)
        return versions[-1] if versions else None
    
    def set_production_model(self, model_name: str, version: str):
        """Set a model version as production."""
        for v in self.registry[model_name]["versions"]:
            v["status"] = "archived"
            if v["version"] == version:
                v["status"] = "production"
        self._save_registry()
        logger.info(f"Set {model_name} v{version} as production")
