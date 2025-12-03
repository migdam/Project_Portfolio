"""
Root Cause Analysis Engine
Identifies why benefits over/underperform using correlation analysis and explainability
"""
import sqlite3
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from scipy.stats import pearsonr, spearmanr
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class RootCauseAnalyzer:
    """
    Performs root cause analysis for benefit variances:
    - Correlation analysis between features and outcomes
    - Feature importance via Random Forest
    - SHAP-like explainability (simplified)
    - Natural language insight generation
    """
    
    def __init__(self, db_path: str = "data/benefit_tracking.db"):
        """Initialize analyzer with database connection"""
        self.db_path = db_path
        self.scaler = StandardScaler()
        self.model = None
    
    def perform_root_cause_analysis(
        self,
        project_id: Optional[str] = None,
        benefit_category: Optional[str] = None,
        threshold_variance_pct: float = -20.0
    ) -> Dict:
        """
        Perform comprehensive root cause analysis
        
        Args:
            project_id: Specific project to analyze (None = all underperformers)
            benefit_category: Specific category to analyze
            threshold_variance_pct: Variance threshold (default -20% = 20% underperformance)
        
        Returns:
            Dict with root causes and contributing factors
        """
        conn = sqlite3.connect(self.db_path)
        
        # Get variance data
        query = """
            SELECT 
                v.project_id,
                v.benefit_category,
                v.planned_amount,
                v.actual_amount,
                v.variance_amount,
                v.variance_pct,
                v.realization_rate,
                bvh.benefit_lag_months,
                bvh.status
            FROM v_benefit_variance v
            LEFT JOIN benefit_variance_history bvh 
                ON v.project_id = bvh.project_id 
                AND v.benefit_category = bvh.benefit_category
            WHERE v.variance_pct < ?
        """
        
        params = [threshold_variance_pct]
        
        if project_id:
            query += " AND v.project_id = ?"
            params.append(project_id)
        
        if benefit_category:
            query += " AND v.benefit_category = ?"
            params.append(benefit_category)
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        if df.empty:
            return {
                'status': 'NO_UNDERPERFORMANCE',
                'message': f'No projects with variance below {threshold_variance_pct}%'
            }
        
        # Analyze root causes
        root_causes = []
        
        for _, row in df.iterrows():
            causes = self._identify_causes(row)
            root_causes.append({
                'project_id': row['project_id'],
                'benefit_category': row['benefit_category'],
                'variance_pct': round(row['variance_pct'], 1),
                'realization_rate': round(row['realization_rate'], 1),
                'causes': causes,
                'severity': self._categorize_severity(row['variance_pct'])
            })
        
        # Aggregate patterns
        patterns = self._aggregate_patterns(root_causes)
        
        return {
            'status': 'SUCCESS',
            'cases_analyzed': len(root_causes),
            'threshold': threshold_variance_pct,
            'root_causes': root_causes,
            'common_patterns': patterns
        }
    
    def _identify_causes(self, row: pd.Series) -> List[str]:
        """Identify specific causes for variance"""
        causes = []
        
        variance_pct = row['variance_pct']
        lag_months = row.get('benefit_lag_months', 0) or 0
        status = row.get('status', 'Unknown')
        
        # Timing issues
        if lag_months and lag_months > 6:
            causes.append(f"Excessive delay: {lag_months:.1f} months behind schedule")
        elif lag_months > 3:
            causes.append(f"Moderate delay: {lag_months:.1f} months lag")
        
        # Severity of underperformance
        if variance_pct < -50:
            causes.append("Severe underperformance: Less than 50% of planned benefits realized")
        elif variance_pct < -30:
            causes.append("Significant gap: 30-50% below planned benefits")
        elif variance_pct < -20:
            causes.append("Moderate underperformance: 20-30% below target")
        
        # Status-based causes
        if status == 'Delayed':
            causes.append("Project delivery delayed beyond expected timeline")
        elif status == 'AtRisk':
            causes.append("Benefit realization at risk due to implementation issues")
        
        # Category-specific patterns
        category = row['benefit_category']
        if category == 'CostSavings':
            causes.append("Common CostSavings issues: Overestimated automation hours or process adoption resistance")
        elif category == 'Revenue':
            causes.append("Common Revenue issues: Market conditions changed or customer adoption slower than expected")
        elif category == 'Productivity':
            causes.append("Common Productivity issues: Workflow changes not adopted or training insufficient")
        
        if not causes:
            causes.append("Root cause unclear - requires detailed investigation")
        
        return causes
    
    def _categorize_severity(self, variance_pct: float) -> str:
        """Categorize severity of variance"""
        if variance_pct < -50:
            return 'CRITICAL'
        elif variance_pct < -30:
            return 'HIGH'
        elif variance_pct < -20:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _aggregate_patterns(self, root_causes: List[Dict]) -> Dict:
        """Aggregate common patterns across multiple cases"""
        if not root_causes:
            return {}
        
        # Count frequency of each cause
        cause_counts = {}
        for case in root_causes:
            for cause in case['causes']:
                # Extract cause type (before colon)
                cause_type = cause.split(':')[0] if ':' in cause else cause
                cause_counts[cause_type] = cause_counts.get(cause_type, 0) + 1
        
        # Sort by frequency
        sorted_causes = sorted(cause_counts.items(), key=lambda x: x[1], reverse=True)
        
        total_cases = len(root_causes)
        
        patterns = []
        for cause, count in sorted_causes[:5]:  # Top 5
            patterns.append({
                'cause': cause,
                'frequency': count,
                'percentage': round(count / total_cases * 100, 1)
            })
        
        return {
            'total_cases': total_cases,
            'top_patterns': patterns
        }
    
    def analyze_feature_correlation(
        self,
        project_features: pd.DataFrame
    ) -> Dict:
        """
        Analyze correlation between project features and benefit variance
        
        Args:
            project_features: DataFrame with columns [project_id, feature1, feature2, ...]
        
        Returns:
            Dict with correlation analysis
        """
        conn = sqlite3.connect(self.db_path)
        
        query = """
            SELECT 
                v.project_id,
                AVG(v.variance_pct) as avg_variance_pct,
                AVG(v.realization_rate) as avg_realization_rate
            FROM v_benefit_variance v
            GROUP BY v.project_id
        """
        
        variance_data = pd.read_sql_query(query, conn)
        conn.close()
        
        # Merge with features
        merged = variance_data.merge(project_features, on='project_id', how='inner')
        
        if len(merged) < 3:
            return {
                'status': 'INSUFFICIENT_DATA',
                'message': 'Need at least 3 projects with features'
            }
        
        # Calculate correlations for each feature
        correlations = []
        feature_cols = [col for col in merged.columns 
                       if col not in ['project_id', 'avg_variance_pct', 'avg_realization_rate']]
        
        for feature in feature_cols:
            # Skip non-numeric columns
            if not pd.api.types.is_numeric_dtype(merged[feature]):
                continue
            
            # Pearson correlation with variance
            r_pearson, p_pearson = pearsonr(merged[feature], merged['avg_variance_pct'])
            
            # Spearman correlation (rank-based, handles non-linear)
            r_spearman, p_spearman = spearmanr(merged[feature], merged['avg_variance_pct'])
            
            # Determine correlation strength
            strength = 'Weak'
            if abs(r_pearson) > 0.7:
                strength = 'Strong'
            elif abs(r_pearson) > 0.4:
                strength = 'Moderate'
            
            # Determine direction and insight
            if r_pearson > 0:
                direction = 'Positive'
                insight = f"Higher {feature} → Better benefit realization"
            else:
                direction = 'Negative'
                insight = f"Higher {feature} → Worse benefit realization"
            
            correlations.append({
                'feature': feature,
                'pearson_r': round(r_pearson, 3),
                'pearson_p_value': round(p_pearson, 4),
                'spearman_r': round(r_spearman, 3),
                'strength': strength,
                'direction': direction,
                'significant': p_pearson < 0.05,
                'insight': insight if p_pearson < 0.05 else 'Not statistically significant'
            })
        
        # Sort by absolute correlation
        correlations = sorted(correlations, key=lambda x: abs(x['pearson_r']), reverse=True)
        
        return {
            'status': 'SUCCESS',
            'sample_size': len(merged),
            'features_analyzed': len(correlations),
            'correlations': correlations,
            'significant_count': sum(1 for c in correlations if c['significant'])
        }
    
    def train_explainability_model(
        self,
        project_features: pd.DataFrame
    ) -> Dict:
        """
        Train Random Forest model for feature importance (SHAP-like analysis)
        
        Args:
            project_features: DataFrame with project characteristics
        
        Returns:
            Dict with feature importance rankings
        """
        conn = sqlite3.connect(self.db_path)
        
        query = """
            SELECT 
                v.project_id,
                AVG(v.realization_rate) as target_realization_rate
            FROM v_benefit_variance v
            GROUP BY v.project_id
        """
        
        target_data = pd.read_sql_query(query, conn)
        conn.close()
        
        # Merge with features
        merged = target_data.merge(project_features, on='project_id', how='inner')
        
        if len(merged) < 5:
            return {
                'status': 'INSUFFICIENT_DATA',
                'message': 'Need at least 5 projects for training'
            }
        
        # Prepare features and target
        feature_cols = [col for col in merged.columns 
                       if col not in ['project_id', 'target_realization_rate']]
        X = merged[feature_cols].fillna(0)
        y = merged['target_realization_rate']
        
        # Filter numeric columns
        numeric_cols = X.select_dtypes(include=[np.number]).columns
        X = X[numeric_cols]
        
        if len(numeric_cols) == 0:
            return {
                'status': 'NO_NUMERIC_FEATURES',
                'message': 'No numeric features available for modeling'
            }
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train Random Forest
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=5,
            random_state=42
        )
        self.model.fit(X_scaled, y)
        
        # Get feature importance
        importances = self.model.feature_importances_
        
        # Create importance ranking
        importance_ranking = []
        for feature, importance in zip(numeric_cols, importances):
            importance_ranking.append({
                'feature': feature,
                'importance': round(float(importance), 4),
                'importance_pct': round(float(importance * 100), 2)
            })
        
        importance_ranking = sorted(importance_ranking, key=lambda x: x['importance'], reverse=True)
        
        # Model performance
        r2_score = self.model.score(X_scaled, y)
        
        return {
            'status': 'SUCCESS',
            'model_type': 'RandomForestRegressor',
            'r2_score': round(r2_score, 3),
            'sample_size': len(merged),
            'features_used': list(numeric_cols),
            'feature_importance': importance_ranking[:10],  # Top 10
            'all_importance': importance_ranking
        }
    
    def generate_insights(
        self,
        root_cause_analysis: Dict,
        feature_correlation: Optional[Dict] = None
    ) -> List[str]:
        """
        Generate natural language insights from analysis
        
        Args:
            root_cause_analysis: Results from perform_root_cause_analysis()
            feature_correlation: Results from analyze_feature_correlation()
        
        Returns:
            List of insight strings
        """
        insights = []
        
        if root_cause_analysis['status'] == 'SUCCESS':
            cases = root_cause_analysis['cases_analyzed']
            patterns = root_cause_analysis.get('common_patterns', {})
            
            insights.append(f"📊 Analyzed {cases} underperforming cases with variance below {root_cause_analysis['threshold']}%")
            
            if patterns and 'top_patterns' in patterns:
                insights.append(f"\n🔍 Top Root Causes:")
                for pattern in patterns['top_patterns'][:3]:
                    insights.append(f"   • {pattern['cause']}: {pattern['percentage']:.1f}% of cases ({pattern['frequency']} projects)")
            
            # Severity distribution
            severities = {}
            for case in root_cause_analysis.get('root_causes', []):
                sev = case['severity']
                severities[sev] = severities.get(sev, 0) + 1
            
            if severities:
                insights.append(f"\n⚠️  Severity Distribution:")
                for sev, count in sorted(severities.items(), key=lambda x: ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'].index(x[0])):
                    insights.append(f"   • {sev}: {count} projects")
        
        if feature_correlation and feature_correlation.get('status') == 'SUCCESS':
            sig_count = feature_correlation['significant_count']
            insights.append(f"\n📈 Feature Correlation Analysis:")
            insights.append(f"   • {sig_count} statistically significant correlations found")
            
            top_corr = feature_correlation['correlations'][:3]
            for corr in top_corr:
                if corr['significant']:
                    insights.append(f"   • {corr['feature']}: {corr['strength']} {corr['direction']} (r={corr['pearson_r']:.2f}, p={corr['pearson_p_value']:.3f})")
                    insights.append(f"     → {corr['insight']}")
        
        if not insights:
            insights.append("No significant insights generated - data may be insufficient")
        
        return insights


# Demo and testing
if __name__ == "__main__":
    print("=" * 80)
    print("Root Cause Analysis Engine - Demo")
    print("=" * 80)
    
    analyzer = RootCauseAnalyzer(db_path="data/benefit_tracking_demo.db")
    
    print("\n🔍 Performing Root Cause Analysis")
    analysis = analyzer.perform_root_cause_analysis(threshold_variance_pct=-10.0)
    print(f"   Status: {analysis['status']}")
    
    if analysis['status'] == 'SUCCESS':
        print(f"   Cases Analyzed: {analysis['cases_analyzed']}")
        print(f"   Threshold: {analysis['threshold']}%")
        
        if analysis['root_causes']:
            print(f"\n   Root Causes:")
            for case in analysis['root_causes'][:3]:  # Top 3
                print(f"\n   Project: {case['project_id']}")
                print(f"   Variance: {case['variance_pct']:.1f}% (Severity: {case['severity']})")
                print(f"   Causes:")
                for cause in case['causes']:
                    print(f"      • {cause}")
        
        if 'common_patterns' in analysis and analysis['common_patterns']:
            patterns = analysis['common_patterns']
            print(f"\n   Common Patterns ({patterns['total_cases']} cases):")
            for pattern in patterns['top_patterns']:
                print(f"      • {pattern['cause']}: {pattern['percentage']:.1f}% ({pattern['frequency']} projects)")
    else:
        print(f"   Message: {analysis.get('message', 'N/A')}")
    
    print("\n📊 Feature Correlation Analysis")
    # Create sample features
    sample_features = pd.DataFrame({
        'project_id': ['PROJ-AI-2024-001'],
        'budget': [2000000],
        'team_size': [15],
        'duration_months': [12]
    })
    
    correlation = analyzer.analyze_feature_correlation(sample_features)
    print(f"   Status: {correlation['status']}")
    if correlation.get('message'):
        print(f"   Message: {correlation['message']}")
    
    print("\n🤖 Training Explainability Model")
    explainability = analyzer.train_explainability_model(sample_features)
    print(f"   Status: {explainability['status']}")
    if explainability.get('message'):
        print(f"   Message: {explainability['message']}")
    
    print("\n💡 Generating Insights")
    insights = analyzer.generate_insights(analysis, correlation)
    for insight in insights:
        print(insight)
    
    print("\n✅ Demo completed successfully!")
