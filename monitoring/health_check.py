"""Model health monitoring."""

from pathlib import Path
from typing import Dict
from datetime import datetime, timedelta

import pandas as pd
import numpy as np

from utils.logger import setup_logger

logger = setup_logger(__name__)


class ModelHealthChecker:
    """Monitors model health and performance."""
    
    def __init__(self, config: Dict):
        """
        Initialize health checker.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.min_confidence = config["monitoring"]["min_prediction_confidence"]
        self.performance_threshold = config["monitoring"]["performance_degradation_threshold"]
    
    def check_prediction_confidence(self, predictions: np.ndarray, confidences: np.ndarray) -> Dict:
        """
        Check if predictions meet minimum confidence thresholds.
        
        Args:
            predictions: Model predictions
            confidences: Confidence scores
            
        Returns:
            Confidence check report
        """
        logger.info("Checking prediction confidence...")
        
        low_confidence = confidences < self.min_confidence
        low_confidence_pct = low_confidence.sum() / len(confidences)
        
        report = {
            "total_predictions": len(predictions),
            "low_confidence_count": int(low_confidence.sum()),
            "low_confidence_pct": float(low_confidence_pct),
            "avg_confidence": float(confidences.mean()),
            "min_confidence": float(confidences.min()),
            "passed": low_confidence_pct < 0.1  # Fail if >10% low confidence
        }
        
        if not report["passed"]:
            logger.warning(
                f"{report['low_confidence_pct']:.1%} of predictions below "
                f"confidence threshold {self.min_confidence}"
            )
        else:
            logger.info(f"Confidence check passed (avg: {report['avg_confidence']:.3f})")
        
        return report
    
    def check_performance_degradation(
        self,
        current_metrics: Dict[str, float],
        baseline_metrics: Dict[str, float]
    ) -> Dict:
        """
        Check for performance degradation vs. baseline.
        
        Args:
            current_metrics: Current model metrics
            baseline_metrics: Baseline metrics from training
            
        Returns:
            Performance degradation report
        """
        logger.info("Checking for performance degradation...")
        
        report = {
            "metrics_compared": [],
            "degraded_metrics": [],
            "passed": True
        }
        
        for metric_name in current_metrics:
            if metric_name not in baseline_metrics:
                continue
            
            current_value = current_metrics[metric_name]
            baseline_value = baseline_metrics[metric_name]
            
            # Calculate relative change
            if baseline_value != 0:
                change = (current_value - baseline_value) / abs(baseline_value)
            else:
                change = 0
            
            is_degraded = change < -self.performance_threshold
            
            report["metrics_compared"].append({
                "metric": metric_name,
                "current": current_value,
                "baseline": baseline_value,
                "change_pct": float(change * 100),
                "is_degraded": is_degraded
            })
            
            if is_degraded:
                report["degraded_metrics"].append(metric_name)
                report["passed"] = False
                logger.warning(
                    f"Performance degradation in '{metric_name}': "
                    f"{baseline_value:.4f} → {current_value:.4f} ({change:.1%})"
                )
        
        if report["passed"]:
            logger.info("No performance degradation detected")
        
        return report
    
    def check_prediction_distribution(
        self,
        predictions: np.ndarray,
        expected_classes: list = None
    ) -> Dict:
        """
        Check if prediction distribution is reasonable.
        
        Args:
            predictions: Model predictions
            expected_classes: Expected classes for classification models
            
        Returns:
            Distribution check report
        """
        logger.info("Checking prediction distribution...")
        
        unique, counts = np.unique(predictions, return_counts=True)
        distribution = dict(zip(unique, counts / len(predictions)))
        
        report = {
            "distribution": {str(k): float(v) for k, v in distribution.items()},
            "n_unique_values": len(unique),
            "most_common": str(unique[counts.argmax()]),
            "most_common_pct": float(counts.max() / len(predictions))
        }
        
        # Check for extreme imbalance (>95% one class)
        if report["most_common_pct"] > 0.95:
            report["warning"] = f"Extreme imbalance: {report['most_common_pct']:.1%} are '{report['most_common']}'"
            logger.warning(report["warning"])
        
        return report
    
    def run_full_health_check(
        self,
        model_name: str,
        predictions: np.ndarray,
        confidences: np.ndarray,
        current_metrics: Dict[str, float],
        baseline_metrics: Dict[str, float]
    ) -> Dict:
        """
        Run complete health check suite.
        
        Args:
            model_name: Name of model being checked
            predictions: Model predictions
            confidences: Confidence scores
            current_metrics: Current performance metrics
            baseline_metrics: Baseline metrics from training
            
        Returns:
            Complete health check report
        """
        logger.info(f"Running full health check for {model_name}...")
        
        report = {
            "model_name": model_name,
            "timestamp": datetime.now().isoformat(),
            "overall_healthy": True
        }
        
        # Confidence check
        conf_report = self.check_prediction_confidence(predictions, confidences)
        report["confidence_check"] = conf_report
        if not conf_report["passed"]:
            report["overall_healthy"] = False
        
        # Performance degradation
        perf_report = self.check_performance_degradation(current_metrics, baseline_metrics)
        report["performance_check"] = perf_report
        if not perf_report["passed"]:
            report["overall_healthy"] = False
        
        # Prediction distribution
        dist_report = self.check_prediction_distribution(predictions)
        report["distribution_check"] = dist_report
        
        if report["overall_healthy"]:
            logger.info(f"✓ {model_name} health check PASSED")
        else:
            logger.error(f"✗ {model_name} health check FAILED")
        
        return report


def main():
    """CLI entry point for health check."""
    import click
    from utils.config import load_config
    
    @click.command()
    def health_check():
        """Run model health check."""
        config = load_config()
        checker = ModelHealthChecker(config)
        
        print("Model Health Check")
        print("=" * 50)
        print(f"Min confidence threshold: {checker.min_confidence}")
        print(f"Performance degradation threshold: {checker.performance_threshold}")
        print("\nRun with prediction data to perform checks.")
    
    health_check()


if __name__ == "__main__":
    main()
