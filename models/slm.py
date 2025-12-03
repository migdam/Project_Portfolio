"""Success Likelihood Model - Predicts project success probability."""

from typing import Any, Dict, Tuple

import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.metrics import accuracy_score, roc_auc_score, precision_recall_curve
import mlflow

from .base import BaseModel
from utils.logger import setup_logger

logger = setup_logger(__name__)


class SuccessLikelihoodModel(BaseModel):
    """Predicts probability of project success."""
    
    def __init__(self, config: Dict):
        """
        Initialize Success Likelihood Model.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__("slm", config)
        self.model = lgb.LGBMClassifier(
            n_estimators=100,
            max_depth=8,
            learning_rate=0.1,
            num_leaves=31,
            random_state=self.training_config["random_state"],
            n_jobs=-1
        )
    
    def train(self, df: pd.DataFrame, target_column: str = "project_success") -> Dict[str, Any]:
        """
        Train the success prediction model.
        
        Args:
            df: Training DataFrame
            target_column: Name of target variable column (binary: 0/1)
            
        Returns:
            Training metrics
        """
        logger.info("Training Success Likelihood Model...")
        
        # Prepare features
        X, feature_names = self.prepare_features(df)
        y = df[target_column]
        
        # Split data
        X_train, X_test, y_train, y_test = self.split_data(X, y)
        
        # Start MLflow run
        with mlflow.start_run(run_name=f"{self.model_name}_training"):
            # Train model
            self.model.fit(
                X_train, y_train,
                eval_set=[(X_test, y_test)],
                callbacks=[lgb.early_stopping(self.training_config["early_stopping_rounds"])]
            )
            self.is_trained = True
            
            # Predictions
            y_pred = self.model.predict(X_test)
            y_pred_proba = self.model.predict_proba(X_test)[:, 1]
            
            # Metrics
            accuracy = accuracy_score(y_test, y_pred)
            roc_auc = roc_auc_score(y_test, y_pred_proba)
            
            # Log parameters
            mlflow.log_params({
                "n_estimators": self.model.n_estimators,
                "max_depth": self.model.max_depth,
                "learning_rate": self.model.learning_rate,
                "n_features": len(feature_names)
            })
            
            # Log metrics
            mlflow.log_metrics({
                "accuracy": accuracy,
                "roc_auc": roc_auc
            })
            
            # Feature importance
            feature_importance = dict(zip(feature_names, self.model.feature_importances_))
            top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]
            
            logger.info(f"Accuracy: {accuracy:.4f}, ROC-AUC: {roc_auc:.4f}")
            logger.info(f"Top features: {top_features}")
            
            # Cross-validation
            cv_scores = self.cross_validate(X, y)
            mlflow.log_metric("cv_mean_score", cv_scores["mean_score"])
            
            return {
                "accuracy": accuracy,
                "roc_auc": roc_auc,
                "feature_importance": feature_importance,
                "cv_scores": cv_scores
            }
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict success (binary: 0/1).
        
        Args:
            X: Feature matrix
            
        Returns:
            Predicted success labels
        """
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        X_prepared, _ = self.prepare_features(X)
        return self.model.predict(X_prepared)
    
    def predict_with_confidence(self, X: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict success with probability scores.
        
        Args:
            X: Feature matrix
            
        Returns:
            Tuple of (predictions, success_probabilities)
        """
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        X_prepared, _ = self.prepare_features(X)
        predictions = self.model.predict(X_prepared)
        probabilities = self.model.predict_proba(X_prepared)[:, 1]  # Probability of success
        
        return predictions, probabilities
    
    def get_success_probability(self, X: pd.DataFrame) -> np.ndarray:
        """
        Get success probability (0-1 scale).
        
        Args:
            X: Feature matrix
            
        Returns:
            Success probabilities
        """
        _, probabilities = self.predict_with_confidence(X)
        return probabilities
