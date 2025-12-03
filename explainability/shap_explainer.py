"""SHAP-based model explanations."""

from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
import shap
import matplotlib.pyplot as plt

from utils.logger import setup_logger

logger = setup_logger(__name__)


class SHAPExplainer:
    """Generate SHAP explanations for model predictions."""
    
    def __init__(self, model, feature_names: List[str]):
        """
        Initialize SHAP explainer.
        
        Args:
            model: Trained model instance
            feature_names: List of feature names
        """
        self.model = model
        self.feature_names = feature_names
        self.explainer = None
        self.shap_values = None
    
    def fit(self, X_background: pd.DataFrame):
        """
        Fit SHAP explainer on background data.
        
        Args:
            X_background: Background dataset for SHAP
        """
        logger.info("Fitting SHAP explainer...")
        
        # Use TreeExplainer for tree-based models
        if hasattr(self.model, 'tree_'):
            self.explainer = shap.TreeExplainer(self.model)
        else:
            # Use KernelExplainer as fallback
            self.explainer = shap.KernelExplainer(
                self.model.predict,
                shap.sample(X_background, 100)
            )
        
        logger.info("SHAP explainer fitted")
    
    def explain_prediction(
        self,
        X: pd.DataFrame,
        top_n: int = 5
    ) -> List[Dict]:
        """
        Explain individual predictions.
        
        Args:
            X: Features to explain
            top_n: Number of top features to return
            
        Returns:
            List of explanation dictionaries
        """
        if self.explainer is None:
            raise ValueError("Explainer not fitted. Call fit() first.")
        
        logger.info(f"Generating SHAP explanations for {len(X)} samples...")
        
        shap_values = self.explainer.shap_values(X)
        
        # Handle multi-class output
        if isinstance(shap_values, list):
            shap_values = shap_values[0]
        
        explanations = []
        
        for idx in range(len(X)):
            # Get SHAP values for this prediction
            sample_shap = shap_values[idx] if len(shap_values.shape) > 1 else shap_values
            
            # Create feature importance ranking
            feature_impacts = []
            for feat_idx, feat_name in enumerate(self.feature_names):
                feature_impacts.append({
                    "feature": feat_name,
                    "value": float(X.iloc[idx, feat_idx]),
                    "shap_value": float(sample_shap[feat_idx]),
                    "abs_shap": abs(float(sample_shap[feat_idx]))
                })
            
            # Sort by absolute SHAP value
            feature_impacts.sort(key=lambda x: x["abs_shap"], reverse=True)
            
            explanations.append({
                "sample_index": idx,
                "top_features": feature_impacts[:top_n],
                "all_features": feature_impacts
            })
        
        return explanations
    
    def get_feature_importance(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Get global feature importance based on SHAP values.
        
        Args:
            X: Dataset to analyze
            
        Returns:
            DataFrame with feature importance
        """
        if self.explainer is None:
            raise ValueError("Explainer not fitted. Call fit() first.")
        
        shap_values = self.explainer.shap_values(X)
        
        if isinstance(shap_values, list):
            shap_values = shap_values[0]
        
        # Calculate mean absolute SHAP value for each feature
        importance = np.abs(shap_values).mean(axis=0)
        
        importance_df = pd.DataFrame({
            "feature": self.feature_names,
            "importance": importance
        }).sort_values("importance", ascending=False)
        
        return importance_df
    
    def plot_waterfall(
        self,
        X: pd.DataFrame,
        sample_idx: int = 0,
        save_path: str = None
    ):
        """
        Create waterfall plot for a single prediction.
        
        Args:
            X: Features
            sample_idx: Index of sample to explain
            save_path: Optional path to save plot
        """
        if self.explainer is None:
            raise ValueError("Explainer not fitted. Call fit() first.")
        
        shap_values = self.explainer.shap_values(X)
        
        if isinstance(shap_values, list):
            shap_values = shap_values[0]
        
        # Create waterfall plot
        shap.plots.waterfall(
            shap.Explanation(
                values=shap_values[sample_idx],
                base_values=self.explainer.expected_value,
                data=X.iloc[sample_idx].values,
                feature_names=self.feature_names
            )
        )
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
            logger.info(f"Waterfall plot saved to {save_path}")
    
    def plot_summary(
        self,
        X: pd.DataFrame,
        max_display: int = 10,
        save_path: str = None
    ):
        """
        Create summary plot showing feature importance.
        
        Args:
            X: Features
            max_display: Maximum number of features to display
            save_path: Optional path to save plot
        """
        if self.explainer is None:
            raise ValueError("Explainer not fitted. Call fit() first.")
        
        shap_values = self.explainer.shap_values(X)
        
        if isinstance(shap_values, list):
            shap_values = shap_values[0]
        
        plt.figure(figsize=(10, 6))
        shap.summary_plot(
            shap_values,
            X,
            feature_names=self.feature_names,
            max_display=max_display,
            show=False
        )
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
            logger.info(f"Summary plot saved to {save_path}")
        else:
            plt.show()
