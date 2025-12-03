"""Data preprocessing and feature engineering."""

from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder

from utils.logger import setup_logger

logger = setup_logger(__name__)


class DataPreprocessor:
    """Handles data cleaning and feature engineering."""
    
    def __init__(self, config: Dict):
        """
        Initialize preprocessor.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.processed_dir = Path(config["data"]["processed_dir"])
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        self.scaler = StandardScaler()
        self.label_encoders = {}
    
    def clean_project_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and prepare project data.
        
        Args:
            df: Raw project data
            
        Returns:
            Cleaned DataFrame
        """
        logger.info("Cleaning project data...")
        
        # Convert dates
        date_columns = ['start_date', 'end_date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['project_id'])
        
        # Handle missing values
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
        
        categorical_cols = df.select_dtypes(include=['object']).columns
        df[categorical_cols] = df[categorical_cols].fillna('unknown')
        
        logger.info(f"Cleaned project data: {len(df)} rows")
        return df
    
    def engineer_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create temporal features from project data.
        
        Args:
            df: Project DataFrame with date columns
            
        Returns:
            DataFrame with additional temporal features
        """
        logger.info("Engineering temporal features...")
        
        if 'start_date' in df.columns and 'end_date' in df.columns:
            # Project duration
            df['project_duration_days'] = (
                df['end_date'] - df['start_date']
            ).dt.days
            
            # Project age
            df['project_age_days'] = (
                pd.Timestamp.now() - df['start_date']
            ).dt.days
            
            # Extract temporal components
            df['start_year'] = df['start_date'].dt.year
            df['start_quarter'] = df['start_date'].dt.quarter
            df['start_month'] = df['start_date'].dt.month
        
        return df
    
    def engineer_complexity_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create complexity indicator features.
        
        Args:
            df: Project DataFrame
            
        Returns:
            DataFrame with complexity features
        """
        logger.info("Engineering complexity features...")
        
        # Scope change frequency (normalized)
        if 'scope_changes_count' in df.columns and 'project_duration_days' in df.columns:
            df['scope_change_frequency'] = (
                df['scope_changes_count'] / 
                (df['project_duration_days'] + 1)  # Avoid division by zero
            )
        
        # Team size complexity
        if 'team_size' in df.columns:
            df['team_complexity_score'] = np.log1p(df['team_size'])
        
        # Dependency complexity (if available)
        if 'dependency_count' in df.columns:
            df['dependency_complexity'] = np.sqrt(df['dependency_count'])
        
        return df
    
    def engineer_financial_features(
        self,
        project_df: pd.DataFrame,
        financial_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Create financial metrics features.
        
        Args:
            project_df: Project DataFrame
            financial_df: Financial DataFrame
            
        Returns:
            DataFrame with financial features
        """
        logger.info("Engineering financial features...")
        
        # Aggregate financial data by project
        if 'earned_value' in financial_df.columns and 'planned_value' in financial_df.columns:
            ev_metrics = financial_df.groupby('project_id').agg({
                'earned_value': 'sum',
                'planned_value': 'sum',
                'actual_spend': 'sum',
                'planned_spend': 'sum'
            }).reset_index()
            
            # Calculate EV/PV ratio
            ev_metrics['ev_pv_ratio'] = (
                ev_metrics['earned_value'] / 
                (ev_metrics['planned_value'] + 1)
            )
            
            # Calculate budget utilization
            ev_metrics['budget_utilization'] = (
                ev_metrics['actual_spend'] / 
                (ev_metrics['planned_spend'] + 1)
            )
            
            # Calculate burn rate variance
            ev_metrics['burn_rate_variance'] = (
                ev_metrics['actual_spend'] - ev_metrics['planned_spend']
            ) / (ev_metrics['planned_spend'] + 1)
            
            # Merge with project data
            project_df = project_df.merge(
                ev_metrics[['project_id', 'ev_pv_ratio', 'budget_utilization', 'burn_rate_variance']],
                on='project_id',
                how='left'
            )
        
        return project_df
    
    def engineer_risk_features(
        self,
        project_df: pd.DataFrame,
        risk_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Create risk indicator features.
        
        Args:
            project_df: Project DataFrame
            risk_df: Risk DataFrame
            
        Returns:
            DataFrame with risk features
        """
        logger.info("Engineering risk features...")
        
        # Count active risks by project
        active_risks = risk_df[risk_df['status'] != 'closed'].groupby('project_id').size()
        project_df['active_risk_count'] = project_df['project_id'].map(active_risks).fillna(0)
        
        # Calculate average risk severity
        if 'impact_score' in risk_df.columns:
            avg_impact = risk_df.groupby('project_id')['impact_score'].mean()
            project_df['avg_risk_impact'] = project_df['project_id'].map(avg_impact).fillna(0)
        
        # Risk escalation rate
        if 'severity' in risk_df.columns:
            high_severity = risk_df[risk_df['severity'].isin(['high', 'critical'])]
            high_risk_count = high_severity.groupby('project_id').size()
            project_df['high_risk_count'] = project_df['project_id'].map(high_risk_count).fillna(0)
        
        return project_df
    
    def create_target_variables(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create target variables for model training.
        
        Args:
            df: Processed DataFrame
            
        Returns:
            DataFrame with target variables
        """
        logger.info("Creating target variables...")
        
        # Schedule slippage (for PRM)
        if 'project_duration_days' in df.columns and 'baseline_schedule_days' in df.columns:
            df['schedule_slippage_pct'] = (
                (df['project_duration_days'] - df['baseline_schedule_days']) /
                (df['baseline_schedule_days'] + 1)
            )
            
            # Categorize risk level
            df['risk_level'] = pd.cut(
                df['schedule_slippage_pct'],
                bins=[-np.inf, 0.05, 0.15, 0.30, np.inf],
                labels=['low', 'medium', 'high', 'critical']
            )
        
        # Cost overrun (for COP)
        if 'actual_cost' in df.columns and 'planned_budget' in df.columns:
            df['cost_overrun'] = df['actual_cost'] - df['planned_budget']
            df['cost_overrun_pct'] = df['cost_overrun'] / (df['planned_budget'] + 1)
            df['has_cost_overrun'] = (df['cost_overrun'] > 0).astype(int)
        
        # Success outcome (for SLM)
        if 'status' in df.columns:
            success_statuses = ['completed', 'delivered', 'closed_success']
            df['project_success'] = df['status'].isin(success_statuses).astype(int)
        
        return df
    
    def save_processed_data(self, df: pd.DataFrame, filename: str):
        """
        Save processed data to file.
        
        Args:
            df: Processed DataFrame
            filename: Output filename
        """
        output_path = self.processed_dir / filename
        df.to_csv(output_path, index=False)
        logger.info(f"Saved processed data to {output_path}")
