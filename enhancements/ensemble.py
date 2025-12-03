"""Ensemble models for improved predictions."""

import numpy as np
import pandas as pd
from typing import List, Dict

from models import ProjectRiskModel, CostOverrunPredictor, SuccessLikelihoodModel
from utils.logger import setup_logger

logger = setup_logger(__name__)


class EnsembleModel:
    """Combine multiple models for better predictions."""
    
    def __init__(self, models: List, weights: List[float] = None):
        """
        Initialize ensemble.
        
        Args:
            models: List of trained models
            weights: Optional weights for each model
        """
        self.models = models
        self.weights = weights or [1.0 / len(models)] * len(models)
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make ensemble predictions."""
        predictions = []
        
        for model, weight in zip(self.models, self.weights):
            pred = model.predict(X)
            predictions.append(pred * weight)
        
        # Average predictions
        ensemble_pred = np.sum(predictions, axis=0)
        
        logger.info(f"Ensemble prediction from {len(self.models)} models")
        return ensemble_pred
    
    def predict_with_uncertainty(self, X: pd.DataFrame) -> tuple:
        """Predict with ensemble uncertainty."""
        predictions = []
        
        for model in self.models:
            pred = model.predict(X)
            predictions.append(pred)
        
        predictions = np.array(predictions)
        mean_pred = predictions.mean(axis=0)
        std_pred = predictions.std(axis=0)
        
        return mean_pred, std_pred
