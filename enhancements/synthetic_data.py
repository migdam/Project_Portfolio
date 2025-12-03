"""Generate synthetic project data for testing."""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from utils.logger import setup_logger

logger = setup_logger(__name__)


class SyntheticDataGenerator:
    """Generate realistic PPM project data."""
    
    def __init__(self, seed: int = 42):
        """Initialize generator."""
        np.random.seed(seed)
        self.seed = seed
    
    def generate_projects(self, n_projects: int = 100) -> pd.DataFrame:
        """
        Generate synthetic project data.
        
        Args:
            n_projects: Number of projects to generate
            
        Returns:
            DataFrame with synthetic projects
        """
        logger.info(f"Generating {n_projects} synthetic projects...")
        
        # Generate base features
        data = {
            'project_id': [f"PROJ-{i:04d}" for i in range(n_projects)],
            'project_name': [f"Project {i}" for i in range(n_projects)],
            
            # Temporal features
            'start_date': [
                datetime.now() - timedelta(days=np.random.randint(365, 1095))
                for _ in range(n_projects)
            ],
            
            # Complexity features
            'scope_change_frequency': np.random.beta(2, 5, n_projects),
            'milestone_variance': np.random.gamma(2, 2, n_projects),
            'team_size': np.random.randint(3, 50, n_projects),
            'team_experience_score': np.random.uniform(1, 10, n_projects),
            'dependency_count': np.random.poisson(5, n_projects),
            'vendor_risk_score': np.random.beta(2, 8, n_projects) * 100,
            
            # Financial features
            'planned_budget': np.random.lognormal(13, 0.5, n_projects),
            'budget_utilization': np.random.normal(1.0, 0.2, n_projects).clip(0.5, 2.0),
            
            # Duration features
            'baseline_schedule_days': np.random.randint(30, 730, n_projects),
            'phase_duration': np.random.randint(30, 365, n_projects),
        }
        
        df = pd.DataFrame(data)
        
        # Calculate derived features
        df['end_date'] = df['start_date'] + pd.to_timedelta(df['baseline_schedule_days'], unit='D')
        df['actual_cost'] = df['planned_budget'] * df['budget_utilization']
        df['project_duration_days'] = (df['end_date'] - df['start_date']).dt.days
        
        # Generate risk levels based on features
        risk_score = (
            df['scope_change_frequency'] * 30 +
            df['milestone_variance'] * 10 +
            (10 - df['team_experience_score']) * 5 +
            df['vendor_risk_score'] * 0.3
        )
        
        df['risk_level'] = pd.cut(
            risk_score,
            bins=[0, 50, 100, 150, 300],
            labels=['low', 'medium', 'high', 'critical']
        )
        
        # Generate target variables
        df['cost_overrun'] = df['actual_cost'] - df['planned_budget']
        df['cost_overrun_pct'] = df['cost_overrun'] / df['planned_budget']
        df['has_cost_overrun'] = (df['cost_overrun'] > 0).astype(int)
        
        # Success probability (inverse correlation with risk)
        success_prob = 1 - (risk_score / risk_score.max())
        df['project_success'] = (np.random.random(n_projects) < success_prob).astype(int)
        
        # Status
        statuses = ['active', 'completed', 'on_hold', 'cancelled']
        df['status'] = np.random.choice(statuses, n_projects, p=[0.3, 0.5, 0.1, 0.1])
        
        logger.info(f"Generated {len(df)} projects with {len(df.columns)} features")
        return df
    
    def generate_financial_data(self, projects_df: pd.DataFrame) -> pd.DataFrame:
        """Generate financial time series data."""
        financial_data = []
        
        for _, project in projects_df.iterrows():
            n_periods = int(project['project_duration_days'] / 30)  # Monthly
            
            for period in range(n_periods):
                period_date = project['start_date'] + timedelta(days=period * 30)
                
                financial_data.append({
                    'project_id': project['project_id'],
                    'period_date': period_date,
                    'planned_spend': project['planned_budget'] / n_periods,
                    'actual_spend': project['actual_cost'] / n_periods * np.random.uniform(0.8, 1.2),
                    'earned_value': project['planned_budget'] / n_periods * np.random.uniform(0.7, 1.1),
                    'planned_value': project['planned_budget'] / n_periods,
                    'npv': np.random.uniform(-1000000, 5000000),
                    'roi': np.random.uniform(-0.2, 1.5)
                })
        
        return pd.DataFrame(financial_data)
    
    def generate_risk_data(self, projects_df: pd.DataFrame) -> pd.DataFrame:
        """Generate risk and issue logs."""
        risk_data = []
        
        for _, project in projects_df.iterrows():
            n_risks = np.random.poisson(3)
            
            for risk_id in range(n_risks):
                identified_date = project['start_date'] + timedelta(days=np.random.randint(0, project['project_duration_days']))
                
                risk_data.append({
                    'project_id': project['project_id'],
                    'risk_id': f"{project['project_id']}-R{risk_id:02d}",
                    'risk_type': np.random.choice(['technical', 'financial', 'resource', 'vendor']),
                    'severity': np.random.choice(['low', 'medium', 'high', 'critical']),
                    'status': np.random.choice(['open', 'mitigated', 'closed']),
                    'identified_date': identified_date,
                    'resolved_date': identified_date + timedelta(days=np.random.randint(1, 90)) if np.random.random() > 0.3 else None,
                    'impact_score': np.random.uniform(1, 10)
                })
        
        return pd.DataFrame(risk_data)
