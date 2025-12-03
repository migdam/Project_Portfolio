"""Cost Overrun Predictor - Forecasts cost overruns."""

from typing import Any, Dict, Tuple

import numpy as np
import pandas as pd
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import mlflow

from .base import BaseModel
from utils.logger import setup_logger

logger = setup_logger(__name__)


class CostOverrunPredictor(BaseModel):
    """Predicts cost overrun magnitude and probability."""
    
    def __init__(self, config: Dict):
        """
        Initialize Cost Overrun Predictor.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__("cop", config)
        self.model = XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=self.training_config["random_state"],
            n_jobs=-1
        )
    
    def train(self, df: pd.DataFrame, target_column: str = "cost_overrun_pct") -> Dict[str, Any]:
        """
        Train the cost overrun prediction model.
        
        Args:
            df: Training DataFrame
            target_column: Name of target variable column
            
        Returns:
            Training metrics
        """
        logger.info("Training Cost Overrun Predictor...")
        
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
                early_stopping_rounds=self.training_config["early_stopping_rounds"],
                verbose=False
            )
            self.is_trained = True
            
            # Predictions
            y_pred = self.model.predict(X_test)
            
            # Metrics
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            r2 = r2_score(y_test, y_pred)
            
            # Log parameters
            mlflow.log_params({
                "n_estimators": self.model.n_estimators,
                "max_depth": self.model.max_depth,
                "learning_rate": self.model.learning_rate,
                "n_features": len(feature_names)
            })
            
            # Log metrics
            mlflow.log_metrics({
                "mae": mae,
                "rmse": rmse,
                "r2": r2
            })
            
            # Feature importance
            feature_importance = dict(zip(feature_names, self.model.feature_importances_))
            top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]
            
            logger.info(f"MAE: {mae:.4f}, RMSE: {rmse:.4f}, R²: {r2:.4f}")
            logger.info(f"Top features: {top_features}")
            
            # Cross-validation
            cv_scores = self.cross_validate(X, y)
            mlflow.log_metric("cv_mean_score", cv_scores["mean_score"])
            
            return {
                "mae": mae,
                "rmse": rmse,
                "r2": r2,
                "feature_importance": feature_importance,
                "cv_scores": cv_scores
            }
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict cost overrun percentage.
        
        Args:
            X: Feature matrix
            
        Returns:
            Predicted cost overrun percentages
        """
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        X_prepared, _ = self.prepare_features(X)
        return self.model.predict(X_prepared)
    
    def predict_with_confidence(self, X: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict cost overrun with confidence intervals.
        
        Args:
            X: Feature matrix
            
        Returns:
            Tuple of (predictions, confidence_intervals)
        """
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        X_prepared, _ = self.prepare_features(X)
        predictions = self.model.predict(X_prepared)
        
        # Estimate confidence using prediction variability
        # For XGBoost, we use the ntree_limit to get ensemble variance
        n_estimators = self.model.n_estimators
        individual_predictions = []
        
        for i in range(1, min(n_estimators + 1, 50), 5):  # Sample estimators
            pred = self.model.predict(X_prepared, ntree_limit=i)
            individual_predictions.append(pred)
        
        # Calculate confidence as inverse of std deviation
        if len(individual_predictions) > 1:
            pred_std = np.std(individual_predictions, axis=0)
            # Normalize to 0-1 scale (higher is more confident)
            confidence = 1.0 / (1.0 + pred_std)
        else:
            confidence = np.ones(len(predictions)) * 0.5
        
        return predictions, confidence
    
    def predict_overrun_probability(self, X: pd.DataFrame, threshold: float = 0.0) -> np.ndarray:
        """
        Predict probability of cost overrun.
        
        Args:
            X: Feature matrix
            threshold: Overrun threshold (default 0.0 = any overrun)
            
        Returns:
            Probability of overrun exceeding threshold
        """
        predictions = self.predict(X)
        # Simple heuristic: convert predicted percentage to probability
        probabilities = 1 / (1 + np.exp(-5 * (predictions - threshold)))
        return probabilities
