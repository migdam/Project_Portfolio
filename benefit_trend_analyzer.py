"""
Benefit Trend Analyzer
ML-powered detection of benefit realization patterns and trends
"""
import sqlite3
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


class BenefitTrendAnalyzer:
    """
    ML-powered analysis of benefit realization patterns:
    - Detects underperforming benefit categories
    - Identifies high-performing projects
    - Clusters similar outcomes
    - Detects anomalies in benefit delivery
    - Predicts future realization patterns
    """
    
    def __init__(self, db_path: str = "data/benefit_tracking.db"):
        """Initialize analyzer with database connection"""
        self.db_path = db_path
        self.scaler = StandardScaler()
        self.rf_model = None
        self.isolation_forest = None
        self.kmeans = None
    
    def detect_underperforming_categories(
        self,
        threshold_pct: float = 70.0
    ) -> Dict:
        """
        Identify benefit categories with low realization rates
        
        Args:
            threshold_pct: Realization rate threshold (default 70%)
        
        Returns:
            Dict with underperforming categories and statistics
        """
        conn = sqlite3.connect(self.db_path)
        
        query = """
            SELECT 
                benefit_category,
                COUNT(DISTINCT project_id) as project_count,
                AVG(realization_rate) as avg_realization_rate,
                MIN(realization_rate) as min_realization_rate,
                MAX(realization_rate) as max_realization_rate,
                SUM(planned_amount) as total_planned,
                SUM(actual_amount) as total_realized,
                SUM(variance_amount) as total_variance
            FROM v_benefit_variance
            GROUP BY benefit_category
            HAVING avg_realization_rate < ?
            ORDER BY avg_realization_rate ASC
        """
        
        df = pd.read_sql_query(query, conn, params=[threshold_pct])
        conn.close()
        
        if df.empty:
            return {
                'status': 'SUCCESS',
                'underperforming_count': 0,
                'categories': [],
                'message': f'No categories below {threshold_pct}% threshold'
            }
        
        categories = []
        for _, row in df.iterrows():
            # Calculate severity
            gap = threshold_pct - row['avg_realization_rate']
            if gap > 30:
                severity = 'CRITICAL'
            elif gap > 20:
                severity = 'HIGH'
            elif gap > 10:
                severity = 'MEDIUM'
            else:
                severity = 'LOW'
            
            categories.append({
                'benefit_category': row['benefit_category'],
                'avg_realization_rate': round(row['avg_realization_rate'], 1),
                'project_count': int(row['project_count']),
                'total_planned': float(row['total_planned']),
                'total_realized': float(row['total_realized']),
                'total_variance': float(row['total_variance']),
                'severity': severity,
                'gap_from_threshold': round(gap, 1)
            })
        
        return {
            'status': 'SUCCESS',
            'threshold': threshold_pct,
            'underperforming_count': len(categories),
            'categories': categories,
            'total_missed_value': sum(cat['total_variance'] for cat in categories if cat['total_variance'] < 0)
        }
    
    def identify_overperforming_projects(
        self,
        threshold_pct: float = 110.0,
        min_benefit_amount: float = 100000
    ) -> Dict:
        """
        Find projects that exceeded benefit expectations
        
        Args:
            threshold_pct: Minimum realization rate (default 110%)
            min_benefit_amount: Minimum planned benefit to include
        
        Returns:
            Dict with high-performing projects and common factors
        """
        conn = sqlite3.connect(self.db_path)
        
        query = """
            SELECT 
                project_id,
                AVG(realization_rate) as avg_realization_rate,
                SUM(planned_amount) as total_planned,
                SUM(actual_amount) as total_realized,
                SUM(variance_amount) as total_variance,
                COUNT(DISTINCT benefit_category) as benefit_categories
            FROM v_benefit_variance
            WHERE planned_amount >= ?
            GROUP BY project_id
            HAVING avg_realization_rate >= ?
            ORDER BY avg_realization_rate DESC
        """
        
        df = pd.read_sql_query(query, conn, params=[min_benefit_amount, threshold_pct])
        conn.close()
        
        if df.empty:
            return {
                'status': 'SUCCESS',
                'high_performer_count': 0,
                'projects': []
            }
        
        projects = []
        for _, row in df.iterrows():
            # Performance tier
            rate = row['avg_realization_rate']
            if rate >= 130:
                tier = 'EXCEPTIONAL'
            elif rate >= 120:
                tier = 'EXCELLENT'
            elif rate >= 110:
                tier = 'GOOD'
            else:
                tier = 'ABOVE_TARGET'
            
            projects.append({
                'project_id': row['project_id'],
                'avg_realization_rate': round(rate, 1),
                'total_planned': float(row['total_planned']),
                'total_realized': float(row['total_realized']),
                'total_variance': float(row['total_variance']),
                'benefit_categories': int(row['benefit_categories']),
                'performance_tier': tier
            })
        
        # Calculate summary statistics
        avg_rate = df['avg_realization_rate'].mean()
        median_rate = df['avg_realization_rate'].median()
        total_excess_value = df['total_variance'].sum()
        
        return {
            'status': 'SUCCESS',
            'high_performer_count': len(projects),
            'projects': projects,
            'summary': {
                'avg_realization_rate': round(avg_rate, 1),
                'median_realization_rate': round(median_rate, 1),
                'total_excess_value': float(total_excess_value)
            }
        }
    
    def analyze_benefit_drivers(
        self,
        project_features: Optional[pd.DataFrame] = None
    ) -> Dict:
        """
        Analyze correlation between project features and benefit realization
        
        Args:
            project_features: DataFrame with project characteristics
                            (e.g., budget, duration, team_size, complexity)
        
        Returns:
            Dict with driver analysis and feature importance
        """
        conn = sqlite3.connect(self.db_path)
        
        # Get benefit realization data
        query = """
            SELECT 
                v.project_id,
                AVG(v.realization_rate) as avg_realization_rate,
                SUM(v.planned_amount) as total_planned,
                COUNT(DISTINCT v.benefit_category) as benefit_category_count,
                AVG(COALESCE(bvh.benefit_lag_months, 0)) as avg_lag_months
            FROM v_benefit_variance v
            LEFT JOIN benefit_variance_history bvh 
                ON v.project_id = bvh.project_id 
                AND v.benefit_category = bvh.benefit_category
            GROUP BY v.project_id
        """
        
        benefit_data = pd.read_sql_query(query, conn)
        conn.close()
        
        if benefit_data.empty:
            return {'status': 'NO_DATA', 'message': 'No benefit data available'}
        
        # If no external features provided, use internal metrics
        if project_features is None:
            features = benefit_data[[
                'total_planned', 
                'benefit_category_count',
                'avg_lag_months'
            ]].fillna(0)
            
            target = benefit_data['avg_realization_rate']
            feature_names = list(features.columns)
        else:
            # Merge with provided features
            merged = benefit_data.merge(
                project_features, 
                on='project_id', 
                how='inner'
            )
            
            if merged.empty:
                return {'status': 'NO_DATA', 'message': 'No matching project features'}
            
            feature_cols = [col for col in merged.columns 
                           if col not in ['project_id', 'avg_realization_rate']]
            features = merged[feature_cols].fillna(0)
            target = merged['avg_realization_rate']
            feature_names = feature_cols
        
        # Train Random Forest to identify important drivers
        if len(features) < 5:
            return {
                'status': 'INSUFFICIENT_DATA',
                'message': f'Need at least 5 projects, got {len(features)}'
            }
        
        # Scale features
        X_scaled = self.scaler.fit_transform(features)
        
        # Train model
        self.rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=5,
            random_state=42
        )
        
        # Convert continuous target to classes (bins)
        target_bins = pd.cut(target, bins=[0, 70, 90, 110, 200], 
                            labels=['Low', 'Medium', 'High', 'Exceptional'])
        
        self.rf_model.fit(X_scaled, target_bins)
        
        # Get feature importance
        importances = self.rf_model.feature_importances_
        
        drivers = []
        for name, importance in zip(feature_names, importances):
            if importance > 0.01:  # Only significant features
                drivers.append({
                    'feature': name,
                    'importance': round(float(importance), 3),
                    'importance_pct': round(float(importance * 100), 1)
                })
        
        drivers = sorted(drivers, key=lambda x: x['importance'], reverse=True)
        
        return {
            'status': 'SUCCESS',
            'model_accuracy': round(self.rf_model.score(X_scaled, target_bins), 3),
            'sample_size': len(features),
            'top_drivers': drivers[:10],
            'all_drivers': drivers
        }
    
    def cluster_similar_outcomes(
        self,
        n_clusters: int = 4
    ) -> Dict:
        """
        Group projects by similar benefit realization patterns
        
        Args:
            n_clusters: Number of clusters to create
        
        Returns:
            Dict with cluster assignments and characteristics
        """
        conn = sqlite3.connect(self.db_path)
        
        query = """
            SELECT 
                v.project_id,
                AVG(v.realization_rate) as avg_realization_rate,
                SUM(v.planned_amount) as total_planned,
                SUM(v.variance_amount) as total_variance,
                AVG(COALESCE(bvh.benefit_lag_months, 0)) as avg_lag_months,
                COUNT(DISTINCT v.benefit_category) as benefit_categories
            FROM v_benefit_variance v
            LEFT JOIN benefit_variance_history bvh 
                ON v.project_id = bvh.project_id 
                AND v.benefit_category = bvh.benefit_category
            GROUP BY v.project_id
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if len(df) < n_clusters:
            return {
                'status': 'INSUFFICIENT_DATA',
                'message': f'Need at least {n_clusters} projects, got {len(df)}'
            }
        
        # Prepare features for clustering
        features = df[[
            'avg_realization_rate',
            'total_planned',
            'total_variance',
            'avg_lag_months',
            'benefit_categories'
        ]].fillna(0)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(features)
        
        # Perform clustering
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        df['cluster'] = self.kmeans.fit_predict(X_scaled)
        
        # Analyze each cluster
        clusters = []
        for cluster_id in range(n_clusters):
            cluster_df = df[df['cluster'] == cluster_id]
            
            # Cluster characteristics
            avg_rate = cluster_df['avg_realization_rate'].mean()
            
            # Label cluster
            if avg_rate >= 110:
                label = 'High Performers'
            elif avg_rate >= 90:
                label = 'On Track'
            elif avg_rate >= 70:
                label = 'At Risk'
            else:
                label = 'Underperformers'
            
            clusters.append({
                'cluster_id': int(cluster_id),
                'label': label,
                'project_count': len(cluster_df),
                'avg_realization_rate': round(avg_rate, 1),
                'avg_planned': round(cluster_df['total_planned'].mean(), 0),
                'avg_variance': round(cluster_df['total_variance'].mean(), 0),
                'avg_lag_months': round(cluster_df['avg_lag_months'].mean(), 1),
                'project_ids': cluster_df['project_id'].tolist()[:10]  # Top 10
            })
        
        clusters = sorted(clusters, key=lambda x: x['avg_realization_rate'], reverse=True)
        
        return {
            'status': 'SUCCESS',
            'n_clusters': n_clusters,
            'total_projects': len(df),
            'clusters': clusters
        }
    
    def detect_anomalies(self, contamination: float = 0.1) -> Dict:
        """
        Detect anomalous benefit realization patterns
        
        Args:
            contamination: Expected proportion of outliers (default 10%)
        
        Returns:
            Dict with anomalous projects and characteristics
        """
        conn = sqlite3.connect(self.db_path)
        
        query = """
            SELECT 
                v.project_id,
                AVG(v.realization_rate) as avg_realization_rate,
                SUM(v.planned_amount) as total_planned,
                SUM(v.variance_amount) as total_variance,
                AVG(COALESCE(bvh.benefit_lag_months, 0)) as avg_lag_months
            FROM v_benefit_variance v
            LEFT JOIN benefit_variance_history bvh 
                ON v.project_id = bvh.project_id 
                AND v.benefit_category = bvh.benefit_category
            GROUP BY v.project_id
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if len(df) < 10:
            return {
                'status': 'INSUFFICIENT_DATA',
                'message': 'Need at least 10 projects for anomaly detection'
            }
        
        # Prepare features
        features = df[[
            'avg_realization_rate',
            'total_planned',
            'total_variance',
            'avg_lag_months'
        ]].fillna(0)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(features)
        
        # Detect anomalies using Isolation Forest
        self.isolation_forest = IsolationForest(
            contamination=contamination,
            random_state=42
        )
        
        df['anomaly'] = self.isolation_forest.fit_predict(X_scaled)
        df['anomaly_score'] = self.isolation_forest.score_samples(X_scaled)
        
        # Get anomalies (prediction = -1)
        anomalies_df = df[df['anomaly'] == -1].copy()
        
        if anomalies_df.empty:
            return {
                'status': 'SUCCESS',
                'anomaly_count': 0,
                'anomalies': []
            }
        
        anomalies = []
        for _, row in anomalies_df.iterrows():
            # Determine anomaly type
            rate = row['avg_realization_rate']
            variance = row['total_variance']
            lag = row['avg_lag_months']
            
            anomaly_type = []
            if rate > 150:
                anomaly_type.append('EXCEPTIONAL_OVERPERFORMANCE')
            elif rate < 30:
                anomaly_type.append('SEVERE_UNDERPERFORMANCE')
            
            if abs(variance) > 1000000:
                anomaly_type.append('EXTREME_VARIANCE')
            
            if lag > 6:
                anomaly_type.append('EXCESSIVE_LAG')
            elif lag < -6:
                anomaly_type.append('EXCEPTIONALLY_EARLY')
            
            anomalies.append({
                'project_id': row['project_id'],
                'avg_realization_rate': round(rate, 1),
                'total_variance': round(variance, 0),
                'avg_lag_months': round(lag, 1),
                'anomaly_score': round(float(row['anomaly_score']), 3),
                'anomaly_types': anomaly_type if anomaly_type else ['PATTERN_OUTLIER']
            })
        
        anomalies = sorted(anomalies, key=lambda x: x['anomaly_score'])
        
        return {
            'status': 'SUCCESS',
            'anomaly_count': len(anomalies),
            'anomalies': anomalies,
            'total_projects_analyzed': len(df)
        }


# Demo and testing
if __name__ == "__main__":
    print("=" * 80)
    print("Benefit Trend Analyzer - Demo")
    print("=" * 80)
    
    analyzer = BenefitTrendAnalyzer(db_path="data/benefit_tracking_demo.db")
    
    print("\n🔍 Detecting Underperforming Categories")
    underperforming = analyzer.detect_underperforming_categories(threshold_pct=80)
    print(f"   Status: {underperforming['status']}")
    print(f"   Underperforming Categories: {underperforming['underperforming_count']}")
    if underperforming['categories']:
        for cat in underperforming['categories']:
            print(f"   - {cat['benefit_category']}: {cat['avg_realization_rate']:.1f}% "
                  f"(Severity: {cat['severity']})")
    
    print("\n🌟 Identifying High Performers")
    high_performers = analyzer.identify_overperforming_projects(threshold_pct=105)
    print(f"   Status: {high_performers['status']}")
    print(f"   High Performers: {high_performers['high_performer_count']}")
    if high_performers['projects']:
        for proj in high_performers['projects'][:5]:
            print(f"   - {proj['project_id']}: {proj['avg_realization_rate']:.1f}% "
                  f"({proj['performance_tier']})")
    
    print("\n📊 Analyzing Benefit Drivers")
    drivers = analyzer.analyze_benefit_drivers()
    if drivers['status'] == 'SUCCESS':
        print(f"   Model Accuracy: {drivers['model_accuracy']:.1%}")
        print(f"   Sample Size: {drivers['sample_size']} projects")
        print(f"   Top Drivers:")
        for driver in drivers['top_drivers'][:5]:
            print(f"   - {driver['feature']}: {driver['importance_pct']:.1f}% importance")
    else:
        print(f"   Status: {drivers['status']} - {drivers.get('message', 'N/A')}")
    
    print("\n🔗 Clustering Similar Outcomes")
    clusters = analyzer.cluster_similar_outcomes(n_clusters=3)
    if clusters['status'] == 'SUCCESS':
        print(f"   Total Projects: {clusters['total_projects']}")
        print(f"   Clusters:")
        for cluster in clusters['clusters']:
            print(f"   - {cluster['label']}: {cluster['project_count']} projects, "
                  f"Avg Rate: {cluster['avg_realization_rate']:.1f}%")
    else:
        print(f"   Status: {clusters['status']} - {clusters.get('message', 'N/A')}")
    
    print("\n⚠️  Detecting Anomalies")
    anomalies = analyzer.detect_anomalies(contamination=0.15)
    if anomalies['status'] == 'SUCCESS':
        print(f"   Anomalies Detected: {anomalies['anomaly_count']}")
        if anomalies['anomalies']:
            for anom in anomalies['anomalies'][:3]:
                print(f"   - {anom['project_id']}: Rate {anom['avg_realization_rate']:.1f}% "
                      f"({', '.join(anom['anomaly_types'])})")
    else:
        print(f"   Status: {anomalies['status']} - {anomalies.get('message', 'N/A')}")
    
    print("\n✅ Demo completed successfully!")
