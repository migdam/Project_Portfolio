"""Automated model retraining scheduler."""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
import json
import pandas as pd

from models import ProjectRiskModel, CostOverrunPredictor, SuccessLikelihoodModel
from monitoring.drift_detection import DriftDetector
from monitoring.health_check import ModelHealthChecker
from utils.logger import setup_logger
from utils.config import load_config

logger = setup_logger(__name__)


class RetrainingScheduler:
    """Manages automated model retraining."""
    
    def __init__(self, config: Dict):
        """
        Initialize retraining scheduler.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.retraining_interval_days = config["monitoring"]["retraining_schedule_days"]
        self.performance_threshold = config["monitoring"]["performance_degradation_threshold"]
        
        self.metadata_file = Path("models/retraining_metadata.json")
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """Load retraining metadata."""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_metadata(self):
        """Save retraining metadata."""
        self.metadata_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def should_retrain(self, model_name: str) -> tuple[bool, str]:
        """
        Check if model should be retrained.
        
        Args:
            model_name: Name of model to check
            
        Returns:
            Tuple of (should_retrain, reason)
        """
        if model_name not in self.metadata:
            return True, "Never trained"
        
        last_training = datetime.fromisoformat(self.metadata[model_name]["last_training_date"])
        days_since_training = (datetime.now() - last_training).days
        
        # Check schedule
        if days_since_training >= self.retraining_interval_days:
            return True, f"Scheduled retraining ({days_since_training} days since last training)"
        
        # Check performance degradation
        if "performance_metrics" in self.metadata[model_name]:
            baseline = self.metadata[model_name]["baseline_metrics"]
            current = self.metadata[model_name]["performance_metrics"]
            
            for metric in baseline:
                if metric in current:
                    degradation = (baseline[metric] - current[metric]) / baseline[metric]
                    if degradation > self.performance_threshold:
                        return True, f"Performance degradation in {metric}: {degradation:.1%}"
        
        # Check drift
        if "drift_detected" in self.metadata[model_name]:
            if self.metadata[model_name]["drift_detected"]:
                return True, "Data drift detected"
        
        return False, "No retraining needed"
    
    def retrain_model(
        self,
        model_name: str,
        training_data: pd.DataFrame,
        target_column: str
    ) -> Dict:
        """
        Retrain a model.
        
        Args:
            model_name: Name of model to retrain
            training_data: Training data
            target_column: Target column name
            
        Returns:
            Training results
        """
        logger.info(f"Retraining {model_name}...")
        
        # Initialize model
        model_classes = {
            'prm': ProjectRiskModel,
            'cop': CostOverrunPredictor,
            'slm': SuccessLikelihoodModel
        }
        
        if model_name not in model_classes:
            raise ValueError(f"Unknown model: {model_name}")
        
        model = model_classes[model_name](self.config)
        
        # Train model
        results = model.train(training_data, target_column=target_column)
        
        # Save model
        model.save_model("models/artifacts")
        
        # Update metadata
        self.metadata[model_name] = {
            "last_training_date": datetime.now().isoformat(),
            "baseline_metrics": results,
            "training_samples": len(training_data),
            "version": self.metadata.get(model_name, {}).get("version", 0) + 1
        }
        self._save_metadata()
        
        logger.info(f"Model {model_name} retrained successfully")
        return results
    
    def check_all_models(self) -> Dict[str, Dict]:
        """
        Check retraining status for all models.
        
        Returns:
            Dictionary with status for each model
        """
        logger.info("Checking retraining status for all models...")
        
        status = {}
        
        for model_name in ['prm', 'cop', 'slm']:
            should_retrain, reason = self.should_retrain(model_name)
            
            status[model_name] = {
                "should_retrain": should_retrain,
                "reason": reason,
                "last_training": self.metadata.get(model_name, {}).get("last_training_date", "Never"),
                "version": self.metadata.get(model_name, {}).get("version", 0)
            }
            
            if should_retrain:
                logger.warning(f"{model_name}: {reason}")
            else:
                logger.info(f"{model_name}: {reason}")
        
        return status
    
    def update_drift_status(self, model_name: str, has_drift: bool):
        """
        Update drift detection status.
        
        Args:
            model_name: Model name
            has_drift: Whether drift was detected
        """
        if model_name not in self.metadata:
            self.metadata[model_name] = {}
        
        self.metadata[model_name]["drift_detected"] = has_drift
        self.metadata[model_name]["drift_check_date"] = datetime.now().isoformat()
        self._save_metadata()
    
    def update_performance(self, model_name: str, metrics: Dict[str, float]):
        """
        Update model performance metrics.
        
        Args:
            model_name: Model name
            metrics: Performance metrics
        """
        if model_name not in self.metadata:
            self.metadata[model_name] = {}
        
        self.metadata[model_name]["performance_metrics"] = metrics
        self.metadata[model_name]["performance_check_date"] = datetime.now().isoformat()
        self._save_metadata()


def main():
    """CLI entry point for retraining scheduler."""
    import click
    
    @click.command()
    @click.option('--check', is_flag=True, help='Check retraining status')
    @click.option('--retrain', help='Retrain specific model (prm/cop/slm)')
    @click.option('--data', help='Path to training data')
    @click.option('--target', help='Target column name')
    def schedule_retraining(check, retrain, data, target):
        """Manage model retraining schedule."""
        config = load_config()
        scheduler = RetrainingScheduler(config)
        
        if check:
            status = scheduler.check_all_models()
            print("\n=== Retraining Status ===")
            for model, info in status.items():
                print(f"\n{model.upper()}:")
                for key, value in info.items():
                    print(f"  {key}: {value}")
        
        elif retrain:
            if not data or not target:
                print("Error: --data and --target are required for retraining")
                return
            
            training_df = pd.read_csv(data)
            results = scheduler.retrain_model(retrain, training_df, target)
            print(f"\n=== Retraining Results for {retrain} ===")
            print(json.dumps(results, indent=2, default=str))
        
        else:
            print("Use --check to check status or --retrain to retrain a model")
    
    schedule_retraining()


if __name__ == "__main__":
    main()
