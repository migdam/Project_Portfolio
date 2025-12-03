"""Data validation and quality checks."""

from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import numpy as np

from utils.logger import setup_logger

logger = setup_logger(__name__)


class DataValidator:
    """Validates data quality before model training."""
    
    def __init__(self, config: Dict):
        """
        Initialize validator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.validated_dir = Path(config["data"]["validated_dir"])
        self.validated_dir.mkdir(parents=True, exist_ok=True)
        
        self.completeness_threshold = config["data"]["completeness_threshold"]
        self.min_historical_years = config["data"]["min_historical_years"]
    
    def check_completeness(self, df: pd.DataFrame, required_columns: List[str]) -> Tuple[bool, Dict]:
        """
        Check data completeness against thresholds.
        
        Args:
            df: DataFrame to validate
            required_columns: List of required column names
            
        Returns:
            Tuple of (is_valid, report_dict)
        """
        logger.info("Checking data completeness...")
        
        report = {
            "total_rows": len(df),
            "column_completeness": {},
            "missing_columns": [],
            "passed": True
        }
        
        # Check for missing columns
        missing_cols = set(required_columns) - set(df.columns)
        if missing_cols:
            report["missing_columns"] = list(missing_cols)
            report["passed"] = False
            logger.warning(f"Missing required columns: {missing_cols}")
        
        # Check completeness for each column
        for col in required_columns:
            if col in df.columns:
                completeness = 1 - (df[col].isna().sum() / len(df))
                report["column_completeness"][col] = completeness
                
                if completeness < self.completeness_threshold:
                    report["passed"] = False
                    logger.warning(
                        f"Column '{col}' completeness {completeness:.2%} "
                        f"below threshold {self.completeness_threshold:.2%}"
                    )
        
        return report["passed"], report
    
    def check_historical_data_window(self, df: pd.DataFrame, date_column: str = "start_date") -> bool:
        """
        Check if data covers minimum historical period.
        
        Args:
            df: DataFrame to validate
            date_column: Name of date column to check
            
        Returns:
            True if data window is sufficient
        """
        logger.info("Checking historical data window...")
        
        if date_column not in df.columns:
            logger.error(f"Date column '{date_column}' not found")
            return False
        
        df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
        date_range = (df[date_column].max() - df[date_column].min()).days / 365.25
        
        if date_range < self.min_historical_years:
            logger.warning(
                f"Historical data window {date_range:.1f} years "
                f"below minimum {self.min_historical_years} years"
            )
            return False
        
        logger.info(f"Historical data window: {date_range:.1f} years")
        return True
    
    def check_outliers(self, df: pd.DataFrame, columns: List[str], z_threshold: float = 3.0) -> Dict:
        """
        Detect outliers using z-score method.
        
        Args:
            df: DataFrame to check
            columns: Columns to check for outliers
            z_threshold: Z-score threshold for outlier detection
            
        Returns:
            Dictionary with outlier report
        """
        logger.info("Checking for outliers...")
        
        report = {"outliers_found": {}}
        
        for col in columns:
            if col in df.columns and df[col].dtype in [np.int64, np.float64]:
                z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
                outliers = z_scores > z_threshold
                outlier_count = outliers.sum()
                
                if outlier_count > 0:
                    report["outliers_found"][col] = {
                        "count": int(outlier_count),
                        "percentage": outlier_count / len(df)
                    }
                    logger.info(f"Found {outlier_count} outliers in '{col}'")
        
        return report
    
    def check_class_balance(self, df: pd.DataFrame, target_column: str, min_samples: int = 30) -> Dict:
        """
        Check class balance for classification targets.
        
        Args:
            df: DataFrame to check
            target_column: Target variable column name
            min_samples: Minimum samples required per class
            
        Returns:
            Dictionary with class balance report
        """
        logger.info(f"Checking class balance for '{target_column}'...")
        
        if target_column not in df.columns:
            return {"error": f"Target column '{target_column}' not found"}
        
        class_counts = df[target_column].value_counts()
        
        report = {
            "class_distribution": class_counts.to_dict(),
            "imbalance_ratio": class_counts.max() / class_counts.min() if len(class_counts) > 1 else 1.0,
            "min_class_samples": int(class_counts.min()),
            "sufficient_samples": class_counts.min() >= min_samples
        }
        
        if not report["sufficient_samples"]:
            logger.warning(
                f"Insufficient samples in smallest class: {class_counts.min()} < {min_samples}"
            )
        
        if report["imbalance_ratio"] > 10:
            logger.warning(f"Severe class imbalance detected: ratio = {report['imbalance_ratio']:.2f}")
        
        return report
    
    def validate_feature_distributions(self, df: pd.DataFrame, numeric_columns: List[str]) -> Dict:
        """
        Validate feature distributions for anomalies.
        
        Args:
            df: DataFrame to validate
            numeric_columns: List of numeric columns to check
            
        Returns:
            Dictionary with distribution report
        """
        logger.info("Validating feature distributions...")
        
        report = {}
        
        for col in numeric_columns:
            if col in df.columns:
                stats = {
                    "mean": float(df[col].mean()),
                    "std": float(df[col].std()),
                    "min": float(df[col].min()),
                    "max": float(df[col].max()),
                    "zeros_pct": float((df[col] == 0).sum() / len(df)),
                    "negative_pct": float((df[col] < 0).sum() / len(df))
                }
                
                # Flag potential issues
                if stats["std"] == 0:
                    stats["warning"] = "No variance (constant column)"
                elif stats["zeros_pct"] > 0.9:
                    stats["warning"] = "More than 90% zeros"
                
                report[col] = stats
        
        return report
    
    def run_full_validation(
        self,
        df: pd.DataFrame,
        required_columns: List[str],
        numeric_columns: List[str],
        target_column: str = None
    ) -> Tuple[bool, Dict]:
        """
        Run complete validation suite.
        
        Args:
            df: DataFrame to validate
            required_columns: Required columns for model
            numeric_columns: Numeric columns to validate
            target_column: Optional target column for classification
            
        Returns:
            Tuple of (is_valid, full_report)
        """
        logger.info("Running full validation suite...")
        
        full_report = {
            "validation_timestamp": pd.Timestamp.now().isoformat(),
            "total_rows": len(df),
            "total_columns": len(df.columns)
        }
        
        # Completeness check
        is_complete, completeness_report = self.check_completeness(df, required_columns)
        full_report["completeness"] = completeness_report
        
        # Historical window check
        has_sufficient_history = self.check_historical_data_window(df)
        full_report["historical_window_passed"] = has_sufficient_history
        
        # Outliers check
        outliers_report = self.check_outliers(df, numeric_columns)
        full_report["outliers"] = outliers_report
        
        # Feature distributions
        distributions = self.validate_feature_distributions(df, numeric_columns)
        full_report["distributions"] = distributions
        
        # Class balance (if target provided)
        if target_column:
            balance_report = self.check_class_balance(df, target_column)
            full_report["class_balance"] = balance_report
        
        # Overall validation result
        is_valid = is_complete and has_sufficient_history
        full_report["overall_passed"] = is_valid
        
        if is_valid:
            logger.info("✓ Data validation PASSED")
        else:
            logger.error("✗ Data validation FAILED")
        
        return is_valid, full_report
    
    def save_validated_data(self, df: pd.DataFrame, filename: str):
        """
        Save validated data to file.
        
        Args:
            df: Validated DataFrame
            filename: Output filename
        """
        output_path = self.validated_dir / filename
        df.to_csv(output_path, index=False)
        logger.info(f"Saved validated data to {output_path}")
