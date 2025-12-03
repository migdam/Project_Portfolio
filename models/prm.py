"""Project Risk Model - Predicts schedule slippage and risk levels."""

from typing import Any, Dict, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, f1_score
import mlflow

from .base import BaseModel
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ProjectRiskModel(BaseModel):
    """Predicts project risk levels (low, medium, high, critical)."""
    
    def __init__(self, config: Dict):
        """
        Initialize Project Risk Model.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__("prm", config)
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=10,
            random_state=self.training_config["random_state"],
            n_jobs=-1
        )
        self.risk_classes = self.model_config.get("output_classes", ["low", "medium", "high", "critical"])
    
    def train(self, df: pd.DataFrame, target_column: str = "risk_level") -> Dict[str, Any]:
        """
        Train the risk prediction model.
        
        Args:
            df: Training DataFrame
            target_column: Name of target variable column
            
        Returns:
            Training metrics
        """
        logger.info("Training Project Risk Model...")
        
        # Prepare features
        X, feature_names = self.prepare_features(df)
        y = df[target_column]
        
        # Split data
        X_train, X_test, y_train, y_test = self.split_data(X, y)
        
        # Start MLflow run
        with mlflow.start_run(run_name=f"{self.model_name}_training"):
            # Train model
            self.model.fit(X_train, y_train)
            self.is_trained = True
            
            # Predictions
            y_pred = self.model.predict(X_test)
            
            # Metrics
            accuracy = accuracy_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred, average='weighted')
            
            # Log parameters
            mlflow.log_params({
                "n_estimators": self.model.n_estimators,
                "max_depth": self.model.max_depth,
                "n_features": len(feature_names)
            })
            
            # Log metrics
            mlflow.log_metrics({
                "accuracy": accuracy,
                "f1_score": f1
            })
            
            # Feature importance
            feature_importance = dict(zip(feature_names, self.model.feature_importances_))
            top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]
            
            logger.info(f"Accuracy: {accuracy:.4f}, F1 Score: {f1:.4f}")
            logger.info(f"Top features: {top_features}")
            
            # Cross-validation
            cv_scores = self.cross_validate(X, y)
            mlflow.log_metric("cv_mean_score", cv_scores["mean_score"])
            
            return {
                "accuracy": accuracy,
                "f1_score": f1,
                "feature_importance": feature_importance,
                "cv_scores": cv_scores,
                "classification_report": classification_report(y_test, y_pred)
            }
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict risk levels.
        
        Args:
            X: Feature matrix
            
        Returns:
            Predicted risk levels
        """
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        X_prepared, _ = self.prepare_features(X)
        return self.model.predict(X_prepared)
    
    def predict_with_confidence(self, X: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict risk levels with confidence scores.
        
        Args:
            X: Feature matrix
            
        Returns:
            Tuple of (predictions, confidence_scores)
        """
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        X_prepared, _ = self.prepare_features(X)
        predictions = self.model.predict(X_prepared)
        probabilities = self.model.predict_proba(X_prepared)
        
        # Confidence is the max probability
        confidence = probabilities.max(axis=1)
        
        return predictions, confidence
    
    def get_risk_score(self, X: pd.DataFrame) -> np.ndarray:
        """
        Get numeric risk score (0-100).
        
        Args:
            X: Feature matrix
            
        Returns:
            Risk scores
        """
        predictions, confidence = self.predict_with_confidence(X)
        
        # Map classes to scores
        risk_score_map = {"low": 25, "medium": 50, "high": 75, "critical": 100}
        scores = np.array([risk_score_map.get(pred, 50) for pred in predictions])
        
        return scores
