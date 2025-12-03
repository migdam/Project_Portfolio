"""Advanced visualizations for portfolio analysis."""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from pathlib import Path

from utils.logger import setup_logger

logger = setup_logger(__name__)


class PortfolioVisualizer:
    """Create advanced portfolio visualizations."""
    
    def __init__(self, output_dir: str = "reports/viz"):
        """Initialize visualizer."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def plot_pareto_frontier(
        self,
        projects_df: pd.DataFrame,
        save_path: str = None
    ) -> go.Figure:
        """
        Plot Pareto frontier of value vs. risk.
        
        Args:
            projects_df: DataFrame with value and risk scores
            save_path: Optional path to save figure
            
        Returns:
            Plotly figure
        """
        fig = go.Figure()
        
        # Scatter plot of all projects
        fig.add_trace(go.Scatter(
            x=projects_df['risk_score'],
            y=projects_df['strategic_value_score'],
            mode='markers',
            name='Projects',
            text=projects_df['project_name'],
            marker=dict(
                size=projects_df['planned_budget'] / 100000,
                color=projects_df['risk_score'],
                colorscale='RdYlGn_r',
                showscale=True,
                colorbar=dict(title="Risk Score")
            )
        ))
        
        fig.update_layout(
            title="Portfolio Pareto Frontier: Value vs. Risk",
            xaxis_title="Risk Score",
            yaxis_title="Strategic Value",
            hovermode='closest',
            template='plotly_white'
        )
        
        if save_path:
            fig.write_html(self.output_dir / save_path)
            logger.info(f"Pareto frontier saved to {save_path}")
        
        return fig
    
    def plot_risk_matrix(
        self,
        projects_df: pd.DataFrame,
        save_path: str = None
    ) -> go.Figure:
        """
        Create risk impact/probability matrix.
        
        Args:
            projects_df: DataFrame with risk data
            save_path: Optional path to save figure
            
        Returns:
            Plotly figure
        """
        fig = go.Figure()
        
        # Create risk zones
        fig.add_shape(type="rect", x0=0, y0=0, x1=50, y1=50, fillcolor="green", opacity=0.2, layer="below", line_width=0)
        fig.add_shape(type="rect", x0=50, y0=0, x1=100, y1=50, fillcolor="yellow", opacity=0.2, layer="below", line_width=0)
        fig.add_shape(type="rect", x0=0, y0=50, x1=50, y1=100, fillcolor="orange", opacity=0.2, layer="below", line_width=0)
        fig.add_shape(type="rect", x0=50, y0=50, x1=100, y1=100, fillcolor="red", opacity=0.2, layer="below", line_width=0)
        
        # Plot projects
        fig.add_trace(go.Scatter(
            x=projects_df['risk_probability'],
            y=projects_df['risk_impact'],
            mode='markers+text',
            text=projects_df['project_id'],
            textposition="top center",
            marker=dict(size=12, color='darkblue')
        ))
        
        fig.update_layout(
            title="Risk Matrix: Impact vs. Probability",
            xaxis=dict(title="Probability", range=[0, 100]),
            yaxis=dict(title="Impact", range=[0, 100]),
            template='plotly_white',
            showlegend=False
        )
        
        if save_path:
            fig.write_html(self.output_dir / save_path)
            logger.info(f"Risk matrix saved to {save_path}")
        
        return fig
    
    def plot_portfolio_map(
        self,
        projects_df: pd.DataFrame,
        save_path: str = None
    ) -> go.Figure:
        """
        Create portfolio bubble chart.
        
        Args:
            projects_df: DataFrame with portfolio data
            save_path: Optional path to save figure
            
        Returns:
            Plotly figure
        """
        fig = px.scatter(
            projects_df,
            x='strategic_alignment',
            y='financial_return',
            size='planned_budget',
            color='risk_level',
            hover_data=['project_name', 'status'],
            title="Portfolio Map: Strategic Alignment vs. Financial Return",
            labels={
                'strategic_alignment': 'Strategic Alignment Score',
                'financial_return': 'Expected Financial Return',
                'risk_level': 'Risk Level'
            },
            color_discrete_map={
                'low': 'green',
                'medium': 'yellow',
                'high': 'orange',
                'critical': 'red'
            }
        )
        
        fig.update_layout(template='plotly_white')
        
        if save_path:
            fig.write_html(self.output_dir / save_path)
            logger.info(f"Portfolio map saved to {save_path}")
        
        return fig
