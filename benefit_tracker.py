"""
Benefit Realization Tracker
Tracks planned vs realized benefits for portfolio projects
"""
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


class BenefitRealizationTracker:
    """
    Tracks benefit realization across portfolio:
    - Stores planned benefits from business cases
    - Records actual benefit delivery
    - Calculates variances and realization rates
    - Identifies trends and lagging benefits
    """
    
    def __init__(self, db_path: str = "data/benefit_tracking.db"):
        """Initialize tracker with database connection"""
        self.db_path = db_path
        self._ensure_database()
    
    def _ensure_database(self):
        """Create database and tables if they don't exist"""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        
        # Read and execute schema
        schema_path = Path(__file__).parent / "schema" / "benefit_tracking.sql"
        if schema_path.exists():
            with open(schema_path) as f:
                conn.executescript(f.read())
        
        conn.close()
        logger.info(f"Benefit tracking database initialized at {self.db_path}")
    
    def track_planned_benefit(
        self,
        project_id: str,
        benefit_category: str,
        planned_amount: float,
        baseline_date: str,  # ISO format YYYY-MM-DD
        benefit_subcategory: Optional[str] = None,
        planned_timeline: Optional[str] = None,
        expected_start_date: Optional[str] = None,
        expected_full_date: Optional[str] = None,
        assumptions: Optional[str] = None
    ) -> Dict:
        """
        Record planned benefit from business case
        
        Args:
            project_id: Unique project identifier
            benefit_category: Revenue, CostSavings, Productivity, RiskReduction, Strategic
            planned_amount: Dollar value of planned benefit
            baseline_date: When benefit was planned (YYYY-MM-DD)
            benefit_subcategory: Optional sub-classification
            planned_timeline: When benefits expected (e.g., "Q2-2024")
            expected_start_date: When benefits should start
            expected_full_date: When fully realized
            assumptions: Key assumptions
        
        Returns:
            Dict with status and recorded data
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO benefit_plans (
                    project_id, benefit_category, benefit_subcategory,
                    planned_amount, planned_timeline, baseline_date,
                    expected_start_date, expected_full_date, assumptions,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project_id, benefit_category, benefit_subcategory,
                planned_amount, planned_timeline, baseline_date,
                expected_start_date, expected_full_date, assumptions,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            
            return {
                'status': 'SUCCESS',
                'project_id': project_id,
                'benefit_category': benefit_category,
                'planned_amount': planned_amount,
                'message': f'Planned benefit recorded for {project_id}'
            }
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error recording planned benefit: {e}")
            return {
                'status': 'ERROR',
                'message': str(e)
            }
        finally:
            conn.close()
    
    def record_realized_benefit(
        self,
        project_id: str,
        benefit_category: str,
        actual_amount: float,
        realization_date: str,  # ISO format YYYY-MM-DD
        benefit_subcategory: Optional[str] = None,
        evidence_source: str = "manual",
        evidence_url: Optional[str] = None,
        confidence_score: float = 0.8,
        measurement_method: Optional[str] = None,
        notes: Optional[str] = None,
        recorded_by: Optional[str] = None
    ) -> Dict:
        """
        Record actual benefit delivered
        
        Args:
            project_id: Unique project identifier
            benefit_category: Must match planned benefit category
            actual_amount: Dollar value actually delivered
            realization_date: When benefit was realized (YYYY-MM-DD)
            benefit_subcategory: Optional sub-classification
            evidence_source: finance_extract, survey, audit, manual
            evidence_url: Link to supporting docs
            confidence_score: 0-1 confidence in measurement
            measurement_method: How benefit was measured
            notes: Additional context
            recorded_by: User who recorded
        
        Returns:
            Dict with status and variance information
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Insert actual benefit
            cursor.execute("""
                INSERT INTO benefit_actuals (
                    project_id, benefit_category, benefit_subcategory,
                    actual_amount, realization_date, evidence_source,
                    evidence_url, confidence_score, measurement_method,
                    notes, recorded_by, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project_id, benefit_category, benefit_subcategory,
                actual_amount, realization_date, evidence_source,
                evidence_url, confidence_score, measurement_method,
                notes, recorded_by, datetime.now().isoformat()
            ))
            
            conn.commit()
            
            # Calculate current variance
            variance = self.calculate_variance(project_id, benefit_category, benefit_subcategory)
            
            return {
                'status': 'SUCCESS',
                'project_id': project_id,
                'benefit_category': benefit_category,
                'actual_amount': actual_amount,
                'variance': variance,
                'message': f'Realized benefit recorded for {project_id}'
            }
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error recording realized benefit: {e}")
            return {
                'status': 'ERROR',
                'message': str(e)
            }
        finally:
            conn.close()
    
    def calculate_variance(
        self,
        project_id: str,
        benefit_category: Optional[str] = None,
        benefit_subcategory: Optional[str] = None
    ) -> Dict:
        """
        Calculate variance between planned and realized benefits
        
        Args:
            project_id: Project to analyze
            benefit_category: Optional filter by category
            benefit_subcategory: Optional filter by subcategory
        
        Returns:
            Dict with variance metrics
        """
        conn = sqlite3.connect(self.db_path)
        
        query = """
            SELECT 
                project_id,
                benefit_category,
                benefit_subcategory,
                planned_amount,
                actual_amount,
                variance_amount,
                variance_pct,
                realization_rate
            FROM v_benefit_variance
            WHERE project_id = ?
        """
        
        params = [project_id]
        
        if benefit_category:
            query += " AND benefit_category = ?"
            params.append(benefit_category)
        
        if benefit_subcategory:
            query += " AND benefit_subcategory = ?"
            params.append(benefit_subcategory)
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        if df.empty:
            return {
                'status': 'NO_DATA',
                'message': 'No benefit plan found for this project'
            }
        
        # Aggregate if multiple categories
        total_planned = df['planned_amount'].sum()
        total_actual = df['actual_amount'].sum()
        variance_amount = total_actual - total_planned
        variance_pct = (variance_amount / total_planned * 100) if total_planned > 0 else 0
        realization_rate = (total_actual / total_planned * 100) if total_planned > 0 else 0
        
        return {
            'status': 'SUCCESS',
            'project_id': project_id,
            'total_planned': float(total_planned),
            'total_actual': float(total_actual),
            'variance_amount': float(variance_amount),
            'variance_pct': float(variance_pct),
            'realization_rate': float(realization_rate),
            'by_category': df.to_dict('records')
        }
    
    def get_realization_rate(self, project_id: str) -> float:
        """
        Get overall benefit realization rate for a project
        
        Returns:
            Percentage (0-100+) of planned benefits delivered
        """
        variance = self.calculate_variance(project_id)
        
        if variance['status'] != 'SUCCESS':
            return 0.0
        
        return variance['realization_rate']
    
    def track_benefit_lag(
        self,
        project_id: str,
        benefit_category: Optional[str] = None
    ) -> Dict:
        """
        Calculate how many months behind schedule benefits are
        
        Args:
            project_id: Project to analyze
            benefit_category: Optional filter
        
        Returns:
            Dict with lag metrics
        """
        conn = sqlite3.connect(self.db_path)
        
        query = """
            SELECT 
                bp.project_id,
                bp.benefit_category,
                bp.expected_full_date,
                MAX(ba.realization_date) as latest_actual_date,
                bp.planned_amount,
                COALESCE(SUM(ba.actual_amount), 0) as actual_amount
            FROM benefit_plans bp
            LEFT JOIN benefit_actuals ba 
                ON bp.project_id = ba.project_id 
                AND bp.benefit_category = ba.benefit_category
            WHERE bp.project_id = ?
        """
        
        params = [project_id]
        
        if benefit_category:
            query += " AND bp.benefit_category = ?"
            params.append(benefit_category)
        
        query += " GROUP BY bp.project_id, bp.benefit_category, bp.expected_full_date"
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        if df.empty:
            return {'status': 'NO_DATA'}
        
        lags = []
        for _, row in df.iterrows():
            if pd.notna(row['expected_full_date']) and pd.notna(row['latest_actual_date']):
                expected = datetime.fromisoformat(row['expected_full_date'])
                actual = datetime.fromisoformat(row['latest_actual_date'])
                lag_days = (actual - expected).days
                lag_months = round(lag_days / 30.0, 1)
                
                realization_rate = (row['actual_amount'] / row['planned_amount'] * 100) if row['planned_amount'] > 0 else 0
                
                status = 'OnTrack'
                if lag_months > 3:
                    status = 'Delayed'
                elif lag_months > 1:
                    status = 'AtRisk'
                elif realization_rate > 100:
                    status = 'Exceeded'
                
                lags.append({
                    'benefit_category': row['benefit_category'],
                    'expected_date': row['expected_full_date'],
                    'actual_date': row['latest_actual_date'],
                    'lag_months': lag_months,
                    'status': status,
                    'realization_rate': round(realization_rate, 1)
                })
        
        avg_lag = np.mean([l['lag_months'] for l in lags]) if lags else 0
        
        return {
            'status': 'SUCCESS',
            'project_id': project_id,
            'average_lag_months': round(avg_lag, 1),
            'by_category': lags
        }
    
    def get_portfolio_summary(self) -> Dict:
        """
        Get portfolio-wide benefit realization summary
        
        Returns:
            Dict with portfolio metrics
        """
        conn = sqlite3.connect(self.db_path)
        
        # Overall portfolio metrics
        query = """
            SELECT 
                COUNT(DISTINCT project_id) as project_count,
                SUM(planned_amount) as total_planned,
                SUM(actual_amount) as total_realized,
                AVG(realization_rate) as avg_realization_rate
            FROM v_benefit_variance
        """
        
        portfolio = pd.read_sql_query(query, conn).iloc[0].to_dict()
        
        # By category
        category_query = """
            SELECT * FROM v_category_performance
            ORDER BY total_planned DESC
        """
        
        categories = pd.read_sql_query(category_query, conn).to_dict('records')
        
        # High performers (>= 90% realization)
        high_query = """
            SELECT project_id, avg_realization_rate as realization_rate
            FROM v_project_benefit_summary
            WHERE avg_realization_rate >= 90
            ORDER BY avg_realization_rate DESC
            LIMIT 10
        """
        
        high_performers = pd.read_sql_query(high_query, conn).to_dict('records')
        
        # Underperformers (< 70% realization)
        under_query = """
            SELECT project_id, avg_realization_rate as realization_rate
            FROM v_project_benefit_summary
            WHERE avg_realization_rate < 70
            ORDER BY avg_realization_rate ASC
            LIMIT 10
        """
        
        underperformers = pd.read_sql_query(under_query, conn).to_dict('records')
        
        conn.close()
        
        return {
            'portfolio': portfolio,
            'by_category': categories,
            'high_performers': high_performers,
            'underperformers': underperformers,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_project_details(self, project_id: str) -> Dict:
        """Get detailed benefit tracking for a specific project"""
        variance = self.calculate_variance(project_id)
        lag = self.track_benefit_lag(project_id)
        
        return {
            'project_id': project_id,
            'variance': variance,
            'lag': lag,
            'realization_rate': self.get_realization_rate(project_id)
        }
    
    def snapshot_variance_history(self, snapshot_date: Optional[str] = None):
        """
        Take a snapshot of current variances for historical tracking
        
        Args:
            snapshot_date: Date of snapshot (YYYY-MM-DD), defaults to today
        """
        if snapshot_date is None:
            snapshot_date = datetime.now().strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current variances
        variances = pd.read_sql_query("SELECT * FROM v_benefit_variance", conn)
        
        # Insert into history
        for _, row in variances.iterrows():
            lag = self.track_benefit_lag(row['project_id'], row['benefit_category'])
            lag_months = 0
            status = 'Unknown'
            
            if lag['status'] == 'SUCCESS' and lag['by_category']:
                lag_months = lag['by_category'][0].get('lag_months', 0)
                status = lag['by_category'][0].get('status', 'Unknown')
            
            cursor.execute("""
                INSERT INTO benefit_variance_history (
                    project_id, benefit_category, snapshot_date,
                    planned_amount, actual_amount, variance_amount,
                    variance_pct, realization_rate, benefit_lag_months, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row['project_id'], row['benefit_category'], snapshot_date,
                row['planned_amount'], row['actual_amount'], row['variance_amount'],
                row['variance_pct'], row['realization_rate'], lag_months, status
            ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Variance snapshot saved for {snapshot_date}: {len(variances)} records")


# Demo and testing
if __name__ == "__main__":
    print("=" * 80)
    print("Benefit Realization Tracker - Demo")
    print("=" * 80)
    
    tracker = BenefitRealizationTracker(db_path="data/benefit_tracking_demo.db")
    
    # Track planned benefits for a project
    print("\n📋 Recording Planned Benefits for PROJ-AI-2024-001")
    
    result1 = tracker.track_planned_benefit(
        project_id="PROJ-AI-2024-001",
        benefit_category="CostSavings",
        benefit_subcategory="Automation",
        planned_amount=1500000,
        baseline_date="2024-01-15",
        planned_timeline="Q3-Q4 2024",
        expected_full_date="2024-12-31",
        assumptions="Assumes 5000 hours automated at $100/hr + 25% productivity gain"
    )
    print(f"   Status: {result1['status']}")
    print(f"   Message: {result1['message']}")
    
    result2 = tracker.track_planned_benefit(
        project_id="PROJ-AI-2024-001",
        benefit_category="Revenue",
        benefit_subcategory="CustomerGrowth",
        planned_amount=2000000,
        baseline_date="2024-01-15",
        planned_timeline="2024-2025",
        expected_full_date="2025-06-30"
    )
    
    # Record realized benefits
    print("\n💰 Recording Realized Benefits")
    
    actual1 = tracker.record_realized_benefit(
        project_id="PROJ-AI-2024-001",
        benefit_category="CostSavings",
        benefit_subcategory="Automation",
        actual_amount=1650000,  # 110% of plan
        realization_date="2024-11-30",
        evidence_source="finance_extract",
        confidence_score=0.95,
        measurement_method="Actual labor hours saved × loaded rate",
        recorded_by="finance_team"
    )
    print(f"   Cost Savings Status: {actual1['status']}")
    print(f"   Realization Rate: {actual1['variance']['realization_rate']:.1f}%")
    
    # Calculate variance
    print("\n📊 Variance Analysis")
    variance = tracker.calculate_variance("PROJ-AI-2024-001")
    print(f"   Total Planned: ${variance['total_planned']:,.0f}")
    print(f"   Total Realized: ${variance['total_actual']:,.0f}")
    print(f"   Variance: ${variance['variance_amount']:,.0f} ({variance['variance_pct']:+.1f}%)")
    print(f"   Overall Realization Rate: {variance['realization_rate']:.1f}%")
    
    # Check benefit lag
    print("\n⏱️  Benefit Delivery Timeline")
    lag = tracker.track_benefit_lag("PROJ-AI-2024-001")
    if lag['status'] == 'SUCCESS':
        print(f"   Average Lag: {lag['average_lag_months']} months")
        for cat in lag['by_category']:
            print(f"   {cat['benefit_category']}: {cat['status']} (lag: {cat['lag_months']} months)")
    
    # Portfolio summary
    print("\n📈 Portfolio Summary")
    summary = tracker.get_portfolio_summary()
    port = summary['portfolio']
    print(f"   Projects Tracked: {port['project_count']}")
    print(f"   Total Planned Benefits: ${port['total_planned']:,.0f}")
    print(f"   Total Realized: ${port['total_realized']:,.0f}")
    print(f"   Portfolio Realization Rate: {port['avg_realization_rate']:.1f}%")
    
    print("\n✅ Demo completed successfully!")
