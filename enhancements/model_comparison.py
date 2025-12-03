"""
Model Comparison Dashboard
Visual interface to compare multiple model versions
"""
import pandas as pd
import plotly.graph_objects as go
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class ModelComparison:
    """Compare multiple model versions"""
    
    def __init__(self):
        self.models: Dict[str, Dict] = {}
    
    def add_model(
        self,
        model_id: str,
        model_name: str,
        version: str,
        metrics: Dict[str, float],
        metadata: Dict = None
    ):
        """Add model for comparison"""
        self.models[model_id] = {
            "name": model_name,
            "version": version,
            "metrics": metrics,
            "metadata": metadata or {}
        }
    
    def compare_metrics(self) -> pd.DataFrame:
        """Generate metrics comparison table"""
        data = []
        for model_id, model_info in self.models.items():
            row = {
                "model_id": model_id,
                "name": model_info["name"],
                "version": model_info["version"]
            }
            row.update(model_info["metrics"])
            data.append(row)
        
        return pd.DataFrame(data)
    
    def plot_metrics_comparison(self, metric_names: List[str]):
        """Create radar chart comparing models"""
        df = self.compare_metrics()
        
        fig = go.Figure()
        
        for _, row in df.iterrows():
            fig.add_trace(go.Scatterpolar(
                r=[row[m] for m in metric_names],
                theta=metric_names,
                name=f"{row['name']} v{row['version']}",
                fill='toself'
            ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            title="Model Metrics Comparison"
        )
        
        return fig
    
    def generate_recommendation(self) -> Dict:
        """Recommend best model based on metrics"""
        df = self.compare_metrics()
        
        # Simple scoring: higher is better for all metrics
        df['score'] = df[['accuracy', 'precision', 'recall', 'f1']].mean(axis=1)
        best_idx = df['score'].idxmax()
        best_model = df.loc[best_idx]
        
        return {
            "recommended_model_id": best_model['model_id'],
            "name": best_model['name'],
            "version": best_model['version'],
            "score": best_model['score'],
            "reason": "Highest average metric score"
        }
