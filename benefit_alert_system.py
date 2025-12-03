"""
Benefit Alert System
Predictive early warning system for benefit shortfalls
"""
import sqlite3
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import logging

logger = logging.getLogger(__name__)


class BenefitAlertSystem:
    """
    Predictive alert system for benefit realization:
    - Monitors benefit delivery progress
    - Predicts potential shortfalls 3-6 months ahead
    - Generates early warnings with severity levels
    - Recommends interventions
    - Tracks alert status and resolution
    """
    
    def __init__(self, db_path: str = "data/benefit_tracking.db"):
        """Initialize alert system with database connection"""
        self.db_path = db_path
        self.scaler = StandardScaler()
        self.prediction_model = None
    
    def monitor_benefit_delivery_progress(self) -> Dict:
        """
        Monitor current benefit delivery across portfolio
        
        Returns:
            Dict with monitoring summary and at-risk projects
        """
        conn = sqlite3.connect(self.db_path)
        
        # Get current variance data
        query = """
            SELECT 
                v.project_id,
                v.benefit_category,
                v.planned_amount,
                v.actual_amount,
                v.variance_pct,
                v.realization_rate,
                bvh.benefit_lag_months,
                bvh.status
            FROM v_benefit_variance v
            LEFT JOIN (
                SELECT project_id, benefit_category, 
                       benefit_lag_months, status,
                       MAX(snapshot_date) as latest_date
                FROM benefit_variance_history
                GROUP BY project_id, benefit_category
            ) bvh ON v.project_id = bvh.project_id 
                AND v.benefit_category = bvh.benefit_category
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            return {
                'status': 'NO_DATA',
                'message': 'No benefit data to monitor'
            }
        
        # Categorize by status
        on_track = df[df['realization_rate'] >= 90].shape[0]
        at_risk = df[(df['realization_rate'] >= 70) & (df['realization_rate'] < 90)].shape[0]
        underperforming = df[df['realization_rate'] < 70].shape[0]
        
        # Identify projects with delays
        delayed = df[df['benefit_lag_months'] > 3].copy() if 'benefit_lag_months' in df.columns else pd.DataFrame()
        
        # Projects requiring immediate attention
        critical = df[
            (df['realization_rate'] < 70) | 
            (df['variance_pct'] < -30)
        ].copy()
        
        return {
            'status': 'SUCCESS',
            'monitoring_date': datetime.now().isoformat(),
            'total_benefits_tracked': len(df),
            'status_distribution': {
                'on_track': int(on_track),
                'at_risk': int(at_risk),
                'underperforming': int(underperforming)
            },
            'delayed_benefits': len(delayed),
            'critical_attention_needed': len(critical),
            'critical_details': critical[['project_id', 'benefit_category', 'realization_rate', 'variance_pct']].to_dict('records')[:10]
        }
    
    def predict_benefit_shortfall(
        self,
        project_id: str,
        benefit_category: Optional[str] = None,
        months_ahead: int = 3
    ) -> Dict:
        """
        Predict potential benefit shortfall for a project
        
        Args:
            project_id: Project to analyze
            benefit_category: Specific category (None = all categories)
            months_ahead: Prediction horizon in months (default 3)
        
        Returns:
            Dict with shortfall predictions and risk scores
        """
        conn = sqlite3.connect(self.db_path)
        
        # Get current variance data
        query = """
            SELECT 
                v.project_id,
                v.benefit_category,
                v.planned_amount,
                v.actual_amount,
                v.variance_pct,
                v.realization_rate,
                bvh.benefit_lag_months
            FROM v_benefit_variance v
            LEFT JOIN benefit_variance_history bvh 
                ON v.project_id = bvh.project_id 
                AND v.benefit_category = bvh.benefit_category
            WHERE v.project_id = ?
        """
        
        params = [project_id]
        if benefit_category:
            query += " AND v.benefit_category = ?"
            params.append(benefit_category)
        
        current = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        if current.empty:
            return {
                'status': 'NO_DATA',
                'message': f'No data found for project {project_id}'
            }
        
        predictions = []
        
        for _, row in current.iterrows():
            # Simple trend-based prediction
            current_rate = row['realization_rate']
            lag_months = row.get('benefit_lag_months', 0) or 0
            
            # Predict future realization rate
            # If currently behind schedule, likely to remain behind
            lag_factor = max(0, 1 - (lag_months / 12))  # Penalty for delays
            
            # Assume some recovery but with lag impact
            predicted_rate = current_rate * lag_factor + (100 - current_rate) * 0.3
            predicted_rate = min(predicted_rate, 100)
            
            # Calculate shortfall
            target_rate = 100.0
            predicted_shortfall_pct = target_rate - predicted_rate
            predicted_shortfall_amount = row['planned_amount'] * (predicted_shortfall_pct / 100)
            
            # Risk score (0-100)
            risk_score = min(100, predicted_shortfall_pct + abs(lag_months * 10))
            
            # Determine risk level
            if risk_score >= 70:
                risk_level = 'CRITICAL'
            elif risk_score >= 50:
                risk_level = 'HIGH'
            elif risk_score >= 30:
                risk_level = 'MEDIUM'
            else:
                risk_level = 'LOW'
            
            # Confidence in prediction
            confidence = 0.7 if lag_months > 0 else 0.5
            
            predictions.append({
                'benefit_category': row['benefit_category'],
                'current_realization_rate': round(current_rate, 1),
                'predicted_realization_rate': round(predicted_rate, 1),
                'predicted_shortfall_pct': round(predicted_shortfall_pct, 1),
                'predicted_shortfall_amount': round(predicted_shortfall_amount, 0),
                'risk_score': round(risk_score, 1),
                'risk_level': risk_level,
                'confidence': round(confidence, 2),
                'prediction_horizon_months': months_ahead
            })
        
        return {
            'status': 'SUCCESS',
            'project_id': project_id,
            'prediction_date': datetime.now().isoformat(),
            'months_ahead': months_ahead,
            'predictions': predictions
        }
    
    def generate_early_warning(
        self,
        deviation_threshold: float = 0.15,
        lag_threshold_months: int = 3
    ) -> Dict:
        """
        Generate early warnings for all at-risk benefits
        
        Args:
            deviation_threshold: Variance threshold (default 15%)
            lag_threshold_months: Delay threshold in months
        
        Returns:
            Dict with generated warnings
        """
        conn = sqlite3.connect(self.db_path)
        
        # Find benefits that are off track
        query = """
            SELECT 
                v.project_id,
                v.benefit_category,
                v.planned_amount,
                v.actual_amount,
                v.variance_pct,
                v.realization_rate,
                bvh.benefit_lag_months,
                bvh.status
            FROM v_benefit_variance v
            LEFT JOIN (
                SELECT project_id, benefit_category,
                       benefit_lag_months, status,
                       MAX(snapshot_date) as latest_date
                FROM benefit_variance_history
                GROUP BY project_id, benefit_category
            ) bvh ON v.project_id = bvh.project_id 
                AND v.benefit_category = bvh.benefit_category
            WHERE v.realization_rate < ?
                OR (bvh.benefit_lag_months IS NOT NULL AND bvh.benefit_lag_months > ?)
        """
        
        threshold_rate = (1 - deviation_threshold) * 100
        at_risk = pd.read_sql_query(
            query, 
            conn, 
            params=[threshold_rate, lag_threshold_months]
        )
        conn.close()
        
        if at_risk.empty:
            return {
                'status': 'SUCCESS',
                'warning_count': 0,
                'warnings': [],
                'message': 'No early warnings generated - all benefits on track'
            }
        
        warnings = []
        
        for _, row in at_risk.iterrows():
            # Determine warning severity
            variance = abs(row['variance_pct'])
            lag = row.get('benefit_lag_months', 0) or 0
            
            if variance > 30 or lag > 6:
                severity = 'CRITICAL'
            elif variance > 20 or lag > 4:
                severity = 'HIGH'
            elif variance > 10 or lag > 3:
                severity = 'MEDIUM'
            else:
                severity = 'LOW'
            
            # Generate warning message
            issues = []
            if row['realization_rate'] < 70:
                issues.append(f"Severe underperformance: {row['realization_rate']:.1f}% realized")
            if variance > 15:
                issues.append(f"Significant variance: {variance:.1f}% below target")
            if lag > 3:
                issues.append(f"Delayed delivery: {lag:.1f} months behind")
            
            warning = {
                'project_id': row['project_id'],
                'benefit_category': row['benefit_category'],
                'severity': severity,
                'realization_rate': round(row['realization_rate'], 1),
                'variance_pct': round(row['variance_pct'], 1),
                'lag_months': round(lag, 1),
                'issues': issues,
                'warning_date': datetime.now().isoformat()
            }
            
            warnings.append(warning)
        
        # Sort by severity
        severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        warnings = sorted(warnings, key=lambda x: severity_order[x['severity']])
        
        return {
            'status': 'SUCCESS',
            'warning_count': len(warnings),
            'warnings': warnings,
            'severity_breakdown': {
                'CRITICAL': sum(1 for w in warnings if w['severity'] == 'CRITICAL'),
                'HIGH': sum(1 for w in warnings if w['severity'] == 'HIGH'),
                'MEDIUM': sum(1 for w in warnings if w['severity'] == 'MEDIUM'),
                'LOW': sum(1 for w in warnings if w['severity'] == 'LOW')
            }
        }
    
    def recommend_interventions(
        self,
        project_id: str,
        benefit_category: str,
        risk_score: float
    ) -> List[str]:
        """
        Recommend interventions based on risk level
        
        Args:
            project_id: Project identifier
            benefit_category: Benefit category
            risk_score: Risk score (0-100)
        
        Returns:
            List of recommended interventions
        """
        recommendations = []
        
        # Category-specific interventions
        if benefit_category == 'CostSavings':
            if risk_score >= 70:
                recommendations.extend([
                    "🚨 URGENT: Review automation assumptions - validate actual hours saved",
                    "🚨 Conduct emergency stakeholder review with finance team",
                    "🚨 Consider process redesign if adoption is below 50%"
                ])
            elif risk_score >= 50:
                recommendations.extend([
                    "⚠️  Accelerate change management activities",
                    "⚠️  Provide additional training for end users",
                    "⚠️  Review and adjust benefit measurement approach"
                ])
            else:
                recommendations.extend([
                    "💡 Monitor adoption rates weekly",
                    "💡 Gather user feedback to identify barriers"
                ])
        
        elif benefit_category == 'Revenue':
            if risk_score >= 70:
                recommendations.extend([
                    "🚨 URGENT: Reassess market conditions and demand assumptions",
                    "🚨 Escalate to executive sponsor for strategic review",
                    "🚨 Consider pivoting go-to-market approach"
                ])
            elif risk_score >= 50:
                recommendations.extend([
                    "⚠️  Increase sales and marketing support",
                    "⚠️  Review pricing strategy and customer feedback",
                    "⚠️  Fast-track product improvements based on early adopter input"
                ])
            else:
                recommendations.extend([
                    "💡 Continue monitoring customer acquisition metrics",
                    "💡 Conduct quarterly business reviews"
                ])
        
        elif benefit_category == 'Productivity':
            if risk_score >= 70:
                recommendations.extend([
                    "🚨 URGENT: Conduct workflow analysis - identify adoption blockers",
                    "🚨 Provide intensive hands-on coaching for teams",
                    "🚨 Consider phased rollback if tool is counterproductive"
                ])
            elif risk_score >= 50:
                recommendations.extend([
                    "⚠️  Increase change management resources",
                    "⚠️  Create champion network for peer support",
                    "⚠️  Simplify workflows to reduce complexity"
                ])
            else:
                recommendations.extend([
                    "💡 Track productivity metrics monthly",
                    "💡 Gather continuous user feedback"
                ])
        
        # General interventions based on risk
        if risk_score >= 70:
            recommendations.extend([
                "🚨 Schedule immediate project review with PMO",
                "🚨 Update benefit realization plan with revised targets",
                "🚨 Consider allocating additional resources"
            ])
        elif risk_score >= 50:
            recommendations.append("⚠️  Initiate monthly benefit tracking reviews")
        
        return recommendations
    
    def create_alert(
        self,
        project_id: str,
        benefit_category: str,
        alert_type: str,
        severity: str,
        predicted_shortfall_pct: Optional[float] = None,
        predicted_shortfall_amount: Optional[float] = None,
        confidence: float = 0.7,
        assigned_to: Optional[str] = None
    ) -> Dict:
        """
        Create and persist an alert in the database
        
        Args:
            project_id: Project identifier
            benefit_category: Benefit category
            alert_type: BenefitShortfall, BenefitLag, AnomalyDetected
            severity: CRITICAL, HIGH, MEDIUM, LOW
            predicted_shortfall_pct: Percentage below target
            predicted_shortfall_amount: Dollar amount
            confidence: Confidence in prediction (0-1)
            assigned_to: Person/team assigned
        
        Returns:
            Dict with alert details
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            alert_id = f"ALERT-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{project_id[:8]}"
            alert_date = datetime.now().strftime('%Y-%m-%d')
            expected_impact_date = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
            
            cursor.execute("""
                INSERT INTO benefit_alerts (
                    alert_id, project_id, benefit_category, alert_type, severity,
                    predicted_shortfall_pct, predicted_shortfall_amount,
                    confidence, alert_date, expected_impact_date, assigned_to
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                alert_id, project_id, benefit_category, alert_type, severity,
                predicted_shortfall_pct, predicted_shortfall_amount,
                confidence, alert_date, expected_impact_date, assigned_to
            ))
            
            conn.commit()
            
            return {
                'status': 'SUCCESS',
                'alert_id': alert_id,
                'project_id': project_id,
                'severity': severity,
                'message': f'Alert created for {project_id}'
            }
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error creating alert: {e}")
            return {
                'status': 'ERROR',
                'message': str(e)
            }
        finally:
            conn.close()
    
    def get_active_alerts(self, severity: Optional[str] = None) -> Dict:
        """Get all active (open) alerts"""
        conn = sqlite3.connect(self.db_path)
        
        query = "SELECT * FROM benefit_alerts WHERE status = 'OPEN'"
        
        if severity:
            query += f" AND severity = '{severity}'"
        
        query += " ORDER BY alert_date DESC"
        
        alerts = pd.read_sql_query(query, conn)
        conn.close()
        
        if alerts.empty:
            return {
                'status': 'SUCCESS',
                'alert_count': 0,
                'alerts': []
            }
        
        return {
            'status': 'SUCCESS',
            'alert_count': len(alerts),
            'alerts': alerts.to_dict('records')
        }
    
    def notify_stakeholders(
        self,
        alert: Dict,
        notification_type: str = "email"
    ) -> Dict:
        """
        Simulate stakeholder notification (would integrate with email/Slack in production)
        
        Args:
            alert: Alert dictionary
            notification_type: email, slack, sms
        
        Returns:
            Dict with notification status
        """
        # In production, this would integrate with email/Slack APIs
        notification_message = f"""
        🚨 BENEFIT ALERT: {alert.get('severity', 'UNKNOWN')}
        
        Project: {alert.get('project_id')}
        Benefit Category: {alert.get('benefit_category')}
        Alert Type: {alert.get('alert_type')}
        
        Predicted Shortfall: {alert.get('predicted_shortfall_pct', 0):.1f}%
        Estimated Impact: ${alert.get('predicted_shortfall_amount', 0):,.0f}
        
        Action Required: Review and address immediately
        """
        
        return {
            'status': 'SUCCESS',
            'notification_type': notification_type,
            'recipients': alert.get('assigned_to', 'PMO Team'),
            'message': notification_message,
            'sent_at': datetime.now().isoformat()
        }


# Demo and testing
if __name__ == "__main__":
    print("=" * 80)
    print("Benefit Alert System - Demo")
    print("=" * 80)
    
    alert_system = BenefitAlertSystem(db_path="data/benefit_tracking_demo.db")
    
    print("\n📊 Monitoring Benefit Delivery Progress")
    monitoring = alert_system.monitor_benefit_delivery_progress()
    print(f"   Status: {monitoring['status']}")
    if monitoring['status'] == 'SUCCESS':
        print(f"   Total Benefits Tracked: {monitoring['total_benefits_tracked']}")
        dist = monitoring['status_distribution']
        print(f"   Status: On Track={dist['on_track']}, At Risk={dist['at_risk']}, Underperforming={dist['underperforming']}")
        print(f"   Critical Attention Needed: {monitoring['critical_attention_needed']}")
    
    print("\n🔮 Predicting Benefit Shortfall")
    prediction = alert_system.predict_benefit_shortfall(
        project_id="PROJ-AI-2024-001",
        months_ahead=3
    )
    print(f"   Status: {prediction['status']}")
    if prediction['status'] == 'SUCCESS':
        for pred in prediction['predictions']:
            print(f"\n   Category: {pred['benefit_category']}")
            print(f"   Current Rate: {pred['current_realization_rate']:.1f}%")
            print(f"   Predicted Rate: {pred['predicted_realization_rate']:.1f}%")
            print(f"   Risk Score: {pred['risk_score']:.1f} ({pred['risk_level']})")
            print(f"   Confidence: {pred['confidence']:.0%}")
    
    print("\n⚠️  Generating Early Warnings")
    warnings = alert_system.generate_early_warning(deviation_threshold=0.20, lag_threshold_months=2)
    print(f"   Status: {warnings['status']}")
    print(f"   Warnings Generated: {warnings['warning_count']}")
    if warnings['warning_count'] > 0:
        print(f"   Severity Breakdown: {warnings['severity_breakdown']}")
        for warning in warnings['warnings'][:3]:
            print(f"\n   Project: {warning['project_id']}")
            print(f"   Category: {warning['benefit_category']}")
            print(f"   Severity: {warning['severity']}")
            print(f"   Issues:")
            for issue in warning['issues']:
                print(f"      • {issue}")
    
    print("\n💡 Recommending Interventions")
    recommendations = alert_system.recommend_interventions(
        project_id="PROJ-AI-2024-001",
        benefit_category="Revenue",
        risk_score=75
    )
    print(f"   Recommendations for HIGH risk Revenue benefit:")
    for rec in recommendations[:5]:
        print(f"      {rec}")
    
    print("\n📝 Creating Alert")
    alert_creation = alert_system.create_alert(
        project_id="PROJ-AI-2024-001",
        benefit_category="Revenue",
        alert_type="BenefitShortfall",
        severity="HIGH",
        predicted_shortfall_pct=25.0,
        predicted_shortfall_amount=500000,
        confidence=0.75,
        assigned_to="PMO_Director"
    )
    print(f"   Status: {alert_creation['status']}")
    if alert_creation['status'] == 'SUCCESS':
        print(f"   Alert ID: {alert_creation['alert_id']}")
    
    print("\n📬 Getting Active Alerts")
    active = alert_system.get_active_alerts()
    print(f"   Status: {active['status']}")
    print(f"   Active Alerts: {active['alert_count']}")
    
    print("\n✅ Demo completed successfully!")
