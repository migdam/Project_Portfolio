"""
Feature Store for ML Features
Centralized storage and versioning of engineered features
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import json
import hashlib
import logging

logger = logging.getLogger(__name__)


class FeatureStore:
    """
    Centralized feature store for consistent feature engineering
    Ensures training and inference use identical transformations
    """
    
    def __init__(self, storage_path: str = "data/feature_store"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.feature_registry: Dict[str, Dict] = {}
        self.feature_groups: Dict[str, List[str]] = {}
        self.load_registry()
    
    def load_registry(self):
        """Load feature registry from disk"""
        registry_file = self.storage_path / "registry.json"
        if registry_file.exists():
            with open(registry_file, 'r') as f:
                data = json.load(f)
                self.feature_registry = data.get("features", {})
                self.feature_groups = data.get("feature_groups", {})
            logger.info(f"Loaded {len(self.feature_registry)} features")
    
    def save_registry(self):
        """Save feature registry to disk"""
        registry_file = self.storage_path / "registry.json"
        with open(registry_file, 'w') as f:
            json.dump({
                "features": self.feature_registry,
                "feature_groups": self.feature_groups
            }, f, indent=2)
    
    def register_feature(
        self,
        feature_name: str,
        feature_type: str,
        description: str,
        transformation_fn: str = None,
        dependencies: List[str] = None,
        metadata: Dict = None
    ):
        """Register a new feature definition"""
        
        feature_def = {
            "name": feature_name,
            "type": feature_type,  # numeric, categorical, datetime, text
            "description": description,
            "transformation_fn": transformation_fn,
            "dependencies": dependencies or [],
            "metadata": metadata or {},
            "version": 1,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Check if feature exists and increment version
        if feature_name in self.feature_registry:
            old_version = self.feature_registry[feature_name]["version"]
            feature_def["version"] = old_version + 1
            logger.info(f"Updated feature {feature_name} to version {feature_def['version']}")
        else:
            logger.info(f"Registered new feature {feature_name}")
        
        self.feature_registry[feature_name] = feature_def
        self.save_registry()
        
        return feature_def
    
    def create_feature_group(
        self,
        group_name: str,
        feature_names: List[str],
        description: str = None
    ):
        """Create a logical grouping of features"""
        
        # Validate all features exist
        for feature_name in feature_names:
            if feature_name not in self.feature_registry:
                raise ValueError(f"Feature {feature_name} not registered")
        
        self.feature_groups[group_name] = {
            "features": feature_names,
            "description": description,
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.save_registry()
        logger.info(f"Created feature group {group_name} with {len(feature_names)} features")
        
        return self.feature_groups[group_name]
    
    def compute_features(
        self,
        df: pd.DataFrame,
        feature_names: List[str] = None,
        feature_group: str = None
    ) -> pd.DataFrame:
        """Compute features from raw data"""
        
        if feature_group:
            if feature_group not in self.feature_groups:
                raise ValueError(f"Feature group {feature_group} not found")
            feature_names = self.feature_groups[feature_group]["features"]
        
        if not feature_names:
            raise ValueError("Must specify either feature_names or feature_group")
        
        result_df = df.copy()
        
        for feature_name in feature_names:
            if feature_name not in self.feature_registry:
                logger.warning(f"Feature {feature_name} not registered, skipping")
                continue
            
            feature_def = self.feature_registry[feature_name]
            
            # Check dependencies
            for dep in feature_def["dependencies"]:
                if dep not in result_df.columns:
                    raise ValueError(f"Dependency {dep} not found for feature {feature_name}")
            
            # Apply transformation if specified
            if feature_def["transformation_fn"]:
                try:
                    # Execute transformation (in production, use safer eval or precompiled functions)
                    result_df[feature_name] = eval(feature_def["transformation_fn"], {
                        "df": result_df,
                        "pd": pd,
                        "np": np
                    })
                    logger.debug(f"Computed feature {feature_name}")
                except Exception as e:
                    logger.error(f"Error computing feature {feature_name}: {e}")
                    raise
        
        return result_df
    
    def get_feature_vector(
        self,
        df: pd.DataFrame,
        feature_group: str,
        entity_id: str = None
    ) -> np.ndarray:
        """Get feature vector for a specific entity or all entities"""
        
        if feature_group not in self.feature_groups:
            raise ValueError(f"Feature group {feature_group} not found")
        
        feature_names = self.feature_groups[feature_group]["features"]
        
        # Compute features if not present
        for feature_name in feature_names:
            if feature_name not in df.columns:
                df = self.compute_features(df, [feature_name])
        
        # Extract feature vector
        if entity_id:
            vector = df[df['entity_id'] == entity_id][feature_names].values
            if len(vector) == 0:
                raise ValueError(f"Entity {entity_id} not found")
            return vector[0]
        else:
            return df[feature_names].values
    
    def materialize_features(
        self,
        df: pd.DataFrame,
        feature_group: str,
        output_path: str = None
    ):
        """Pre-compute and store features for faster retrieval"""
        
        features_df = self.compute_features(df, feature_group=feature_group)
        
        if output_path is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            output_path = self.storage_path / f"{feature_group}_{timestamp}.parquet"
        
        features_df.to_parquet(output_path)
        logger.info(f"Materialized {len(features_df)} records to {output_path}")
        
        return output_path
    
    def load_materialized_features(
        self,
        feature_group: str,
        version: str = "latest"
    ) -> pd.DataFrame:
        """Load pre-computed features"""
        
        # Find matching files
        pattern = f"{feature_group}_*.parquet"
        files = list(self.storage_path.glob(pattern))
        
        if not files:
            raise FileNotFoundError(f"No materialized features found for {feature_group}")
        
        if version == "latest":
            file_path = max(files, key=lambda p: p.stat().st_mtime)
        else:
            file_path = self.storage_path / f"{feature_group}_{version}.parquet"
            if not file_path.exists():
                raise FileNotFoundError(f"Version {version} not found")
        
        logger.info(f"Loading features from {file_path}")
        return pd.read_parquet(file_path)
    
    def get_feature_metadata(self, feature_name: str) -> Dict:
        """Get metadata for a specific feature"""
        return self.feature_registry.get(feature_name)
    
    def list_features(self, feature_type: str = None) -> List[Dict]:
        """List all registered features"""
        features = list(self.feature_registry.values())
        
        if feature_type:
            features = [f for f in features if f["type"] == feature_type]
        
        return features
    
    def compute_feature_hash(self, feature_names: List[str]) -> str:
        """Compute hash of feature set for versioning"""
        feature_string = "|".join(sorted(feature_names))
        return hashlib.md5(feature_string.encode()).hexdigest()[:8]


# Pre-defined feature transformations for Portfolio ML
PORTFOLIO_FEATURES = {
    "velocity_trend": {
        "type": "numeric",
        "description": "Project velocity trend over last 3 milestones",
        "transformation_fn": "df['completed_tasks'] / df['planned_tasks']",
        "dependencies": ["completed_tasks", "planned_tasks"]
    },
    "scope_change_rate": {
        "type": "numeric",
        "description": "Rate of scope changes per month",
        "transformation_fn": "df['scope_changes'] / df['project_duration_months']",
        "dependencies": ["scope_changes", "project_duration_months"]
    },
    "burn_rate_variance": {
        "type": "numeric",
        "description": "Variance in monthly burn rate",
        "transformation_fn": "df['actual_burn_rate'] - df['planned_burn_rate']",
        "dependencies": ["actual_burn_rate", "planned_burn_rate"]
    },
    "team_experience_score": {
        "type": "numeric",
        "description": "Weighted team experience score",
        "transformation_fn": "df['avg_years_experience'] * df['team_stability_score']",
        "dependencies": ["avg_years_experience", "team_stability_score"]
    },
    "dependency_risk": {
        "type": "numeric",
        "description": "Risk from project dependencies",
        "transformation_fn": "df['external_dependencies'] * df['vendor_risk_score']",
        "dependencies": ["external_dependencies", "vendor_risk_score"]
    }
}


def initialize_portfolio_feature_store() -> FeatureStore:
    """Initialize feature store with portfolio-specific features"""
    store = FeatureStore()
    
    for feature_name, config in PORTFOLIO_FEATURES.items():
        store.register_feature(
            feature_name=feature_name,
            feature_type=config["type"],
            description=config["description"],
            transformation_fn=config["transformation_fn"],
            dependencies=config["dependencies"]
        )
    
    # Create feature groups
    store.create_feature_group(
        "prm_features",
        ["velocity_trend", "scope_change_rate", "burn_rate_variance", "team_experience_score"],
        "Features for Project Risk Model"
    )
    
    store.create_feature_group(
        "cop_features",
        ["scope_change_rate", "burn_rate_variance", "dependency_risk"],
        "Features for Cost Overrun Predictor"
    )
    
    return store
