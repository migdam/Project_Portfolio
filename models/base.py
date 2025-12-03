"""Base class for all ML models."""

import joblib
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
import mlflow

from utils.logger import setup_logger

logger = setup_logger(__name__)


class BaseModel:
    """Base class for all portfolio ML models."""
    
    def __init__(self, model_name: str, config: Dict):
        """
        Initialize base model.
        
        Args:
            model_name: Name of the model (prm, cop, slm, po)
            config: Configuration dictionary
        """
        self.model_name = model_name
        self.config = config
        self.model_config = config["models"][model_name]
        self.training_config = config["training"]
        
        self.model = None
        self.feature_names = self.model_config.get("features", [])
        self.is_trained = False
        
        # Set up MLflow
        mlflow.set_tracking_uri(config["mlflow"]["tracking_uri"])
        mlflow.set_experiment(config["mlflow"]["experiment_name"])
    
    def prepare_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        Prepare feature matrix from DataFrame.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Tuple of (feature_df, feature_names)
        """
        available_features = [f for f in self.feature_names if f in df.columns]
        
        if len(available_features) < len(self.feature_names):
            missing = set(self.feature_names) - set(available_features)
            logger.warning(f"Missing features: {missing}")
        
        X = df[available_features].copy()
        
        # Handle any remaining NaN values
        X = X.fillna(X.median())
        
        return X, available_features
    
    def split_data(
        self,
        X: pd.DataFrame,
        y: pd.Series
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """
        Split data into train and test sets.
        
        Args:
            X: Feature matrix
            y: Target variable
            
        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        return train_test_split(
            X, y,
            test_size=self.training_config["test_size"],
            random_state=self.training_config["random_state"],
            stratify=y if self.model_config["type"] == "classification" else None
        )
    
    def cross_validate(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """
        Perform cross-validation.
        
        Args:
            X: Feature matrix
            y: Target variable
            
        Returns:
            Dictionary with cross-validation scores
        """
        if self.model is None:
            raise ValueError("Model not initialized")
        
        cv_folds = self.training_config["cv_folds"]
        scores = cross_val_score(
            self.model, X, y,
            cv=cv_folds,
            scoring='accuracy' if self.model_config["type"] == "classification" else 'r2'
        )
        
        return {
            "mean_score": float(scores.mean()),
            "std_score": float(scores.std()),
            "scores": scores.tolist()
        }
    
    def save_model(self, output_dir: str = "models/artifacts"):
        """
        Save trained model to disk.
        
        Args:
            output_dir: Directory to save model
        """
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")
        
        model_dir = Path(output_dir) / self.model_name
        model_dir.mkdir(parents=True, exist_ok=True)
        
        model_path = model_dir / "model.joblib"
        joblib.dump(self.model, model_path)
        
        # Save feature names
        feature_path = model_dir / "features.txt"
        with open(feature_path, "w") as f:
            f.write("\n".join(self.feature_names))
        
        logger.info(f"Model saved to {model_path}")
    
    def load_model(self, model_dir: str = "models/artifacts"):
        """
        Load trained model from disk.
        
        Args:
            model_dir: Directory containing saved model
        """
        model_path = Path(model_dir) / self.model_name / "model.joblib"
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        self.model = joblib.load(model_path)
        self.is_trained = True
        
        # Load feature names
        feature_path = Path(model_dir) / self.model_name / "features.txt"
        if feature_path.exists():
            with open(feature_path, "r") as f:
                self.feature_names = [line.strip() for line in f]
        
        logger.info(f"Model loaded from {model_path}")
    
    def train(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """
        Train the model. To be implemented by subclasses.
        
        Args:
            X: Feature matrix
            y: Target variable
            
        Returns:
            Training metrics
        """
        raise NotImplementedError("Subclass must implement train()")
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Make predictions. To be implemented by subclasses.
        
        Args:
            X: Feature matrix
            
        Returns:
            Predictions
        """
        raise NotImplementedError("Subclass must implement predict()")
    
    def predict_with_confidence(self, X: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Make predictions with confidence scores. To be implemented by subclasses.
        
        Args:
            X: Feature matrix
            
        Returns:
            Tuple of (predictions, confidence_scores)
        """
        raise NotImplementedError("Subclass must implement predict_with_confidence()")
