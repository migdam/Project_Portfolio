"""Model drift detection."""

from typing import Dict, List
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from utils.logger import setup_logger

logger = setup_logger(__name__)


class DriftDetector:
    """Detects data and prediction drift."""
    
    def __init__(self, config: Dict):
        """
        Initialize drift detector.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.drift_threshold = config["monitoring"]["drift_detection_threshold"]
        self.reference_data = None
    
    def set_reference_data(self, df: pd.DataFrame, feature_columns: List[str]):
        """
        Set reference data for drift comparison.
        
        Args:
            df: Reference DataFrame
            feature_columns: Columns to monitor for drift
        """
        self.reference_data = df[feature_columns].copy()
        self.feature_columns = feature_columns
        logger.info(f"Reference data set: {len(df)} rows, {len(feature_columns)} features")
    
    def detect_feature_drift(self, new_data: pd.DataFrame) -> Dict[str, any]:
        """
        Detect drift in feature distributions using KS test.
        
        Args:
            new_data: New data to compare against reference
            
        Returns:
            Drift detection report
        """
        if self.reference_data is None:
            raise ValueError("Reference data not set")
        
        logger.info("Detecting feature drift...")
        
        drift_report = {
            "overall_drift": False,
            "features_with_drift": [],
            "feature_statistics": {}
        }
        
        for col in self.feature_columns:
            if col not in new_data.columns:
                continue
            
            # Kolmogorov-Smirnov test
            statistic, p_value = stats.ks_2samp(
                self.reference_data[col].dropna(),
                new_data[col].dropna()
            )
            
            has_drift = p_value < self.drift_threshold
            
            drift_report["feature_statistics"][col] = {
                "ks_statistic": float(statistic),
                "p_value": float(p_value),
                "has_drift": has_drift,
                "mean_shift": float(new_data[col].mean() - self.reference_data[col].mean()),
                "std_shift": float(new_data[col].std() - self.reference_data[col].std())
            }
            
            if has_drift:
                drift_report["features_with_drift"].append(col)
                drift_report["overall_drift"] = True
                logger.warning(f"Drift detected in feature '{col}' (p={p_value:.4f})")
        
        if drift_report["overall_drift"]:
            logger.warning(f"Drift detected in {len(drift_report['features_with_drift'])} features")
        else:
            logger.info("No significant drift detected")
        
        return drift_report
    
    def detect_prediction_drift(
        self,
        reference_predictions: np.ndarray,
        new_predictions: np.ndarray
    ) -> Dict[str, any]:
        """
        Detect drift in model predictions.
        
        Args:
            reference_predictions: Historical predictions
            new_predictions: Recent predictions
            
        Returns:
            Prediction drift report
        """
        logger.info("Detecting prediction drift...")
        
        # KS test for prediction distributions
        statistic, p_value = stats.ks_2samp(reference_predictions, new_predictions)
        
        has_drift = p_value < self.drift_threshold
        
        report = {
            "has_drift": has_drift,
            "ks_statistic": float(statistic),
            "p_value": float(p_value),
            "mean_shift": float(np.mean(new_predictions) - np.mean(reference_predictions)),
            "std_shift": float(np.std(new_predictions) - np.std(reference_predictions))
        }
        
        if has_drift:
            logger.warning(f"Prediction drift detected (p={p_value:.4f})")
        else:
            logger.info("No prediction drift detected")
        
        return report


def main():
    """CLI entry point for drift detection."""
    import click
    from utils.config import load_config
    
    @click.command()
    @click.option('--model', required=True, help='Model name or "all"')
    @click.option('--reference-data', required=True, help='Path to reference data')
    @click.option('--new-data', required=True, help='Path to new data')
    def detect_drift(model, reference_data, new_data):
        """Detect model drift."""
        config = load_config()
        detector = DriftDetector(config)
        
        ref_df = pd.read_csv(reference_data)
        new_df = pd.read_csv(new_data)
        
        if model == "all":
            models = list(config["models"].keys())
        else:
            models = [model]
        
        for model_name in models:
            features = config["models"][model_name]["features"]
            detector.set_reference_data(ref_df, features)
            report = detector.detect_feature_drift(new_df)
            
            print(f"\n=== Drift Report: {model_name} ===")
            print(f"Overall drift: {report['overall_drift']}")
            print(f"Features with drift: {report['features_with_drift']}")
    
    detect_drift()


if __name__ == "__main__":
    main()
