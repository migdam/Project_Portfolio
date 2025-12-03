"""Data ingestion from PPM and finance systems."""

from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
from sqlalchemy import create_engine

from utils.logger import setup_logger

logger = setup_logger(__name__)


class DataIngestion:
    """Handles data extraction from PPM and finance systems."""
    
    def __init__(self, config: Dict):
        """
        Initialize data ingestion.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.raw_dir = Path(config["data"]["raw_dir"])
        self.raw_dir.mkdir(parents=True, exist_ok=True)
    
    def ingest_from_sql(
        self,
        connection_string: str,
        query: str,
        output_filename: str
    ) -> pd.DataFrame:
        """
        Ingest data from SQL database.
        
        Args:
            connection_string: Database connection string
            query: SQL query to execute
            output_filename: Name of output CSV file
            
        Returns:
            DataFrame with ingested data
        """
        logger.info(f"Ingesting data from database...")
        
        engine = create_engine(connection_string)
        df = pd.read_sql(query, engine)
        
        # Save to raw directory
        output_path = self.raw_dir / output_filename
        df.to_csv(output_path, index=False)
        logger.info(f"Saved {len(df)} rows to {output_path}")
        
        return df
    
    def ingest_from_csv(
        self,
        file_path: str,
        output_filename: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Ingest data from CSV file.
        
        Args:
            file_path: Path to input CSV file
            output_filename: Optional name for output file in raw directory
            
        Returns:
            DataFrame with ingested data
        """
        logger.info(f"Ingesting data from {file_path}...")
        
        df = pd.read_csv(file_path)
        
        if output_filename:
            output_path = self.raw_dir / output_filename
            df.to_csv(output_path, index=False)
            logger.info(f"Saved {len(df)} rows to {output_path}")
        
        return df
    
    def ingest_project_data(self, source: str) -> pd.DataFrame:
        """
        Ingest project data from PPM system.
        
        Expected columns:
        - project_id, project_name, start_date, end_date, status
        - planned_budget, actual_cost, baseline_schedule_days
        - milestone_count, scope_changes_count, team_size
        
        Args:
            source: Data source (file path or connection string)
            
        Returns:
            DataFrame with project data
        """
        if source.endswith('.csv'):
            return self.ingest_from_csv(source, "projects.csv")
        else:
            query = """
                SELECT 
                    project_id, project_name, start_date, end_date, status,
                    planned_budget, actual_cost, baseline_schedule_days,
                    milestone_count, scope_changes_count, team_size
                FROM projects
                WHERE start_date >= DATEADD(year, -3, GETDATE())
            """
            return self.ingest_from_sql(source, query, "projects.csv")
    
    def ingest_financial_data(self, source: str) -> pd.DataFrame:
        """
        Ingest financial data from finance systems.
        
        Expected columns:
        - project_id, period_date, planned_spend, actual_spend
        - earned_value, planned_value, npv, roi
        
        Args:
            source: Data source (file path or connection string)
            
        Returns:
            DataFrame with financial data
        """
        if source.endswith('.csv'):
            return self.ingest_from_csv(source, "financials.csv")
        else:
            query = """
                SELECT 
                    project_id, period_date, 
                    planned_spend, actual_spend,
                    earned_value, planned_value,
                    npv, roi
                FROM project_financials
                WHERE period_date >= DATEADD(year, -3, GETDATE())
            """
            return self.ingest_from_sql(source, query, "financials.csv")
    
    def ingest_risk_data(self, source: str) -> pd.DataFrame:
        """
        Ingest risk and issue logs.
        
        Expected columns:
        - project_id, risk_id, risk_type, severity, status
        - identified_date, resolved_date, impact_score
        
        Args:
            source: Data source (file path or connection string)
            
        Returns:
            DataFrame with risk data
        """
        if source.endswith('.csv'):
            return self.ingest_from_csv(source, "risks.csv")
        else:
            query = """
                SELECT 
                    project_id, risk_id, risk_type, severity, status,
                    identified_date, resolved_date, impact_score
                FROM project_risks
                WHERE identified_date >= DATEADD(year, -3, GETDATE())
            """
            return self.ingest_from_sql(source, query, "risks.csv")
