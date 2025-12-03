"""
A/B Testing Framework for ML Models
Compare performance of different model versions in production
"""
import hashlib
import random
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ModelVariant:
    """Represents a model variant in an A/B test"""
    variant_id: str
    model_path: str
    traffic_percentage: float
    description: str
    metadata: Dict = None


@dataclass
class ExperimentResult:
    """Stores A/B test results"""
    variant_id: str
    predictions_count: int
    accuracy: float
    latency_ms: float
    error_rate: float
    user_feedback_score: Optional[float] = None


class ABTestManager:
    """Manages A/B testing experiments for ML models"""
    
    def __init__(self, config_path: str = "config/ab_tests.json"):
        self.config_path = Path(config_path)
        self.experiments: Dict[str, Dict] = {}
        self.results: Dict[str, List[ExperimentResult]] = {}
        self.load_experiments()
    
    def load_experiments(self):
        """Load experiment configurations"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self.experiments = json.load(f)
            logger.info(f"Loaded {len(self.experiments)} experiments")
    
    def save_experiments(self):
        """Save experiment configurations"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.experiments, f, indent=2)
    
    def create_experiment(
        self,
        experiment_id: str,
        model_name: str,
        variants: List[ModelVariant],
        start_date: str,
        end_date: str = None,
        success_metric: str = "accuracy"
    ):
        """Create new A/B testing experiment"""
        
        # Validate traffic percentages
        total_traffic = sum(v.traffic_percentage for v in variants)
        if abs(total_traffic - 100.0) > 0.01:
            raise ValueError(f"Traffic percentages must sum to 100%, got {total_traffic}%")
        
        experiment = {
            "experiment_id": experiment_id,
            "model_name": model_name,
            "variants": [
                {
                    "variant_id": v.variant_id,
                    "model_path": v.model_path,
                    "traffic_percentage": v.traffic_percentage,
                    "description": v.description,
                    "metadata": v.metadata or {}
                }
                for v in variants
            ],
            "start_date": start_date,
            "end_date": end_date,
            "success_metric": success_metric,
            "status": "active",
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.experiments[experiment_id] = experiment
        self.results[experiment_id] = []
        self.save_experiments()
        
        logger.info(f"Created experiment {experiment_id} with {len(variants)} variants")
        return experiment
    
    def get_variant_for_request(
        self,
        experiment_id: str,
        user_id: str = None,
        project_id: str = None
    ) -> Optional[ModelVariant]:
        """Determine which variant to use for a request"""
        
        if experiment_id not in self.experiments:
            return None
        
        experiment = self.experiments[experiment_id]
        
        if experiment["status"] != "active":
            return None
        
        # Check if experiment has ended
        if experiment.get("end_date"):
            end_date = datetime.fromisoformat(experiment["end_date"])
            if datetime.utcnow() > end_date:
                self.stop_experiment(experiment_id)
                return None
        
        # Use consistent hashing for user-based assignment
        if user_id:
            hash_value = int(hashlib.md5(f"{experiment_id}:{user_id}".encode()).hexdigest(), 16)
            bucket = (hash_value % 100) / 100.0
        else:
            bucket = random.random()
        
        # Select variant based on traffic percentage
        cumulative = 0.0
        for variant_config in experiment["variants"]:
            cumulative += variant_config["traffic_percentage"] / 100.0
            if bucket <= cumulative:
                return ModelVariant(
                    variant_id=variant_config["variant_id"],
                    model_path=variant_config["model_path"],
                    traffic_percentage=variant_config["traffic_percentage"],
                    description=variant_config["description"],
                    metadata=variant_config.get("metadata", {})
                )
        
        # Fallback to first variant
        return ModelVariant(**experiment["variants"][0])
    
    def record_result(
        self,
        experiment_id: str,
        variant_id: str,
        accuracy: float,
        latency_ms: float,
        error_occurred: bool = False,
        user_feedback: Optional[float] = None
    ):
        """Record experiment result"""
        
        if experiment_id not in self.results:
            self.results[experiment_id] = []
        
        # Find existing result for variant or create new
        variant_result = None
        for result in self.results[experiment_id]:
            if result.variant_id == variant_id:
                variant_result = result
                break
        
        if variant_result is None:
            variant_result = ExperimentResult(
                variant_id=variant_id,
                predictions_count=0,
                accuracy=0.0,
                latency_ms=0.0,
                error_rate=0.0,
                user_feedback_score=None
            )
            self.results[experiment_id].append(variant_result)
        
        # Update metrics (running average)
        n = variant_result.predictions_count
        variant_result.predictions_count += 1
        variant_result.accuracy = (variant_result.accuracy * n + accuracy) / (n + 1)
        variant_result.latency_ms = (variant_result.latency_ms * n + latency_ms) / (n + 1)
        
        if error_occurred:
            variant_result.error_rate = (variant_result.error_rate * n + 1.0) / (n + 1)
        else:
            variant_result.error_rate = (variant_result.error_rate * n) / (n + 1)
        
        if user_feedback is not None:
            if variant_result.user_feedback_score is None:
                variant_result.user_feedback_score = user_feedback
            else:
                variant_result.user_feedback_score = (
                    variant_result.user_feedback_score * n + user_feedback
                ) / (n + 1)
    
    def get_results(self, experiment_id: str) -> List[ExperimentResult]:
        """Get results for an experiment"""
        return self.results.get(experiment_id, [])
    
    def get_winner(
        self,
        experiment_id: str,
        metric: str = "accuracy",
        min_predictions: int = 100
    ) -> Optional[str]:
        """Determine winning variant based on specified metric"""
        
        results = self.get_results(experiment_id)
        
        # Filter variants with minimum predictions
        valid_results = [r for r in results if r.predictions_count >= min_predictions]
        
        if not valid_results:
            return None
        
        # Find best variant based on metric
        if metric == "accuracy":
            winner = max(valid_results, key=lambda r: r.accuracy)
        elif metric == "latency":
            winner = min(valid_results, key=lambda r: r.latency_ms)
        elif metric == "error_rate":
            winner = min(valid_results, key=lambda r: r.error_rate)
        elif metric == "user_feedback":
            winner = max(
                [r for r in valid_results if r.user_feedback_score is not None],
                key=lambda r: r.user_feedback_score,
                default=None
            )
            if winner is None:
                return None
        else:
            raise ValueError(f"Unknown metric: {metric}")
        
        return winner.variant_id
    
    def stop_experiment(self, experiment_id: str):
        """Stop an experiment"""
        if experiment_id in self.experiments:
            self.experiments[experiment_id]["status"] = "stopped"
            self.experiments[experiment_id]["stopped_at"] = datetime.utcnow().isoformat()
            self.save_experiments()
            logger.info(f"Stopped experiment {experiment_id}")
    
    def promote_variant(self, experiment_id: str, variant_id: str):
        """Promote winning variant to production"""
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        variant = next(
            (v for v in experiment["variants"] if v["variant_id"] == variant_id),
            None
        )
        
        if not variant:
            raise ValueError(f"Variant {variant_id} not found in experiment")
        
        self.experiments[experiment_id]["status"] = "completed"
        self.experiments[experiment_id]["winner"] = variant_id
        self.experiments[experiment_id]["completed_at"] = datetime.utcnow().isoformat()
        self.save_experiments()
        
        logger.info(f"Promoted variant {variant_id} from experiment {experiment_id}")
        return variant["model_path"]
    
    def get_experiment_summary(self, experiment_id: str) -> Dict:
        """Get comprehensive experiment summary"""
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            return None
        
        results = self.get_results(experiment_id)
        
        return {
            "experiment": experiment,
            "results": [
                {
                    "variant_id": r.variant_id,
                    "predictions_count": r.predictions_count,
                    "accuracy": round(r.accuracy, 4),
                    "latency_ms": round(r.latency_ms, 2),
                    "error_rate": round(r.error_rate, 4),
                    "user_feedback_score": round(r.user_feedback_score, 2) if r.user_feedback_score else None
                }
                for r in results
            ],
            "winner": self.get_winner(experiment_id, experiment["success_metric"]),
            "status": experiment["status"]
        }


# Global instance
ab_test_manager = ABTestManager()
