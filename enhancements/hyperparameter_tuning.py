"""Hyperparameter tuning with Optuna."""

import optuna
from optuna.pruners import MedianPruner
import pandas as pd
from sklearn.model_selection import cross_val_score

from models import ProjectRiskModel, CostOverrunPredictor, SuccessLikelihoodModel
from utils.logger import setup_logger
from utils.config import load_config

logger = setup_logger(__name__)


class HyperparameterTuner:
    """Optimize model hyperparameters using Optuna."""
    
    def __init__(self, model_name: str, config: dict):
        """Initialize tuner."""
        self.model_name = model_name
        self.config = config
        self.best_params = None
    
    def objective_prm(self, trial: optuna.Trial) -> float:
        """Objective function for PRM."""
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 50, 300),
            'max_depth': trial.suggest_int('max_depth', 5, 20),
            'min_samples_split': trial.suggest_int('min_samples_split', 2, 20),
        }
        
        model = ProjectRiskModel(self.config)
        model.model.set_params(**params)
        
        # Cross-validation score
        scores = cross_val_score(model.model, self.X, self.y, cv=5, scoring='f1_weighted')
        return scores.mean()
    
    def tune(self, X: pd.DataFrame, y: pd.Series, n_trials: int = 50) -> dict:
        """
        Run hyperparameter tuning.
        
        Args:
            X: Features
            y: Target
            n_trials: Number of optimization trials
            
        Returns:
            Best hyperparameters
        """
        self.X = X
        self.y = y
        
        logger.info(f"Starting hyperparameter tuning for {self.model_name}...")
        
        study = optuna.create_study(
            direction='maximize',
            pruner=MedianPruner()
        )
        
        objective_map = {
            'prm': self.objective_prm
        }
        
        study.optimize(objective_map[self.model_name], n_trials=n_trials)
        
        self.best_params = study.best_params
        logger.info(f"Best params: {self.best_params}")
        logger.info(f"Best score: {study.best_value:.4f}")
        
        return self.best_params
