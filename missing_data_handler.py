"""
Missing Data Handler for Portfolio ML

Handles incomplete data for projects with various imputation strategies:
1. Historical mean/median imputation
2. Similar project imputation (based on size, domain, team)
3. Conservative defaults (assume worst case for risk)
4. Confidence scoring based on data completeness
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from database import PortfolioDB
from datetime import datetime, timedelta

class MissingDataHandler:
    """
    Handles missing data in project analysis with multiple strategies
    """
    
    # Minimum data quality thresholds
    MIN_COMPLETENESS_FOR_ANALYSIS = 0.30  # 30% minimum (must have required fields)
    HIGH_QUALITY_THRESHOLD = 0.85  # 85% for high confidence
    
    # Required vs optional fields
    REQUIRED_FIELDS = ['project_id', 'risk_score']
    OPTIONAL_FIELDS = ['cost_variance', 'success_probability', 'budget', 'team_size', 'duration_months']
    
    def __init__(self, db: PortfolioDB):
        self.db = db
        
    def assess_data_quality(self, project_data: dict) -> Dict:
        """
        Assess the quality and completeness of project data
        
        Returns:
            - completeness: 0.0 to 1.0 (percentage of fields present)
            - quality_level: LOW, MEDIUM, HIGH
            - missing_fields: list of missing field names
            - confidence_penalty: reduction in confidence score
        """
        all_fields = self.REQUIRED_FIELDS + self.OPTIONAL_FIELDS
        
        # Check which fields are present and not None/NaN
        present_fields = []
        missing_fields = []
        
        for field in all_fields:
            value = project_data.get(field)
            if value is not None and value != '' and not (isinstance(value, float) and np.isnan(value)):
                present_fields.append(field)
            else:
                missing_fields.append(field)
        
        # Calculate completeness
        completeness = len(present_fields) / len(all_fields)
        
        # Determine quality level
        if completeness >= self.HIGH_QUALITY_THRESHOLD:
            quality_level = "HIGH"
            confidence_penalty = 0.0
        elif completeness >= self.MIN_COMPLETENESS_FOR_ANALYSIS:
            quality_level = "MEDIUM"
            confidence_penalty = 0.15  # 15% confidence reduction
        else:
            quality_level = "LOW"
            confidence_penalty = 0.35  # 35% confidence reduction
        
        # Check if required fields are missing
        missing_required = [f for f in self.REQUIRED_FIELDS if f in missing_fields]
        
        return {
            'completeness': completeness,
            'quality_level': quality_level,
            'missing_fields': missing_fields,
            'missing_required': missing_required,
            'confidence_penalty': confidence_penalty,
            'can_analyze': len(missing_required) == 0 and completeness >= self.MIN_COMPLETENESS_FOR_ANALYSIS
        }
    
    def impute_missing_values(self, project_data: dict, strategy: str = "auto") -> Tuple[dict, dict]:
        """
        Fill in missing values using various imputation strategies
        
        Strategies:
        - "historical": Use historical mean/median from this project
        - "similar": Use values from similar projects
        - "conservative": Use conservative defaults (worst-case for risk)
        - "auto": Automatically select best strategy
        
        Returns:
            - imputed_data: dict with filled values
            - imputation_log: dict tracking what was imputed and how
        """
        imputed_data = project_data.copy()
        imputation_log = {}
        
        project_id = project_data.get('project_id', 'UNKNOWN')
        
        # Get historical data for this project
        history = self.db.get_project_risk_trend(project_id, days=90) if project_id != 'UNKNOWN' else []
        
        # Impute risk_score (critical field)
        if 'risk_score' not in project_data or project_data.get('risk_score') is None:
            if history and len(history) > 0:
                # Use historical median
                historical_risks = [h['risk_score'] for h in history if 'risk_score' in h]
                imputed_data['risk_score'] = int(np.median(historical_risks)) if historical_risks else 50
                imputation_log['risk_score'] = f"Historical median ({len(historical_risks)} points)"
            else:
                # Conservative default: assume medium risk
                imputed_data['risk_score'] = 50
                imputation_log['risk_score'] = "Conservative default (no history)"
        
        # Impute cost_variance
        if 'cost_variance' not in project_data or project_data.get('cost_variance') is None:
            if history and len(history) > 0:
                historical_costs = [h.get('cost_variance', 0) for h in history]
                imputed_data['cost_variance'] = float(np.median(historical_costs)) if historical_costs else 0.0
                imputation_log['cost_variance'] = f"Historical median ({len(historical_costs)} points)"
            else:
                # Conservative: assume slight overrun
                imputed_data['cost_variance'] = 5.0
                imputation_log['cost_variance'] = "Conservative default (+5% assumed)"
        
        # Impute success_probability
        if 'success_probability' not in project_data or project_data.get('success_probability') is None:
            if history and len(history) > 0:
                historical_success = [h.get('success_probability', 0.7) for h in history]
                imputed_data['success_probability'] = float(np.mean(historical_success)) if historical_success else 0.7
                imputation_log['success_probability'] = f"Historical mean ({len(historical_success)} points)"
            else:
                # Neutral default
                imputed_data['success_probability'] = 0.7
                imputation_log['success_probability'] = "Neutral default (70%)"
        
        # Impute optional metadata fields
        if 'budget' not in project_data or project_data.get('budget') is None:
            # Use similar projects or default
            imputed_data['budget'] = self._impute_from_similar_projects(project_data, 'budget', default=1000000)
            imputation_log['budget'] = "Similar projects or default ($1M)"
        
        if 'team_size' not in project_data or project_data.get('team_size') is None:
            imputed_data['team_size'] = self._impute_from_similar_projects(project_data, 'team_size', default=5)
            imputation_log['team_size'] = "Similar projects or default (5)"
        
        if 'duration_months' not in project_data or project_data.get('duration_months') is None:
            imputed_data['duration_months'] = self._impute_from_similar_projects(project_data, 'duration_months', default=6)
            imputation_log['duration_months'] = "Similar projects or default (6 months)"
        
        return imputed_data, imputation_log
    
    def _impute_from_similar_projects(self, project_data: dict, field: str, default: float) -> float:
        """
        Impute a field value based on similar projects
        
        Similarity based on:
        - Risk score proximity
        - Budget proximity (if available)
        - Domain/type (if available)
        """
        # For now, use default (can be enhanced with similarity search)
        # TODO: Implement proper similar project search
        return default
    
    def analyze_with_missing_data(self, project_data: dict, verbose: bool = False) -> Dict:
        """
        Complete pipeline: assess quality, impute, and analyze project
        
        Returns analysis with:
        - Original data quality assessment
        - Imputed values (if any)
        - Confidence score adjusted for data quality
        - Warning flags for low quality data
        """
        # Step 1: Assess data quality
        quality = self.assess_data_quality(project_data)
        
        if verbose:
            print(f"\n📊 Data Quality Assessment")
            print(f"   Completeness: {quality['completeness']:.1%}")
            print(f"   Quality Level: {quality['quality_level']}")
            print(f"   Missing Fields: {len(quality['missing_fields'])}")
            if quality['missing_fields']:
                print(f"   → {', '.join(quality['missing_fields'])}")
        
        # Step 2: Check if analysis is possible
        if not quality['can_analyze']:
            return {
                'status': 'INSUFFICIENT_DATA',
                'quality': quality,
                'message': f"Cannot analyze: {len(quality['missing_required'])} required fields missing",
                'required_fields_missing': quality['missing_required']
            }
        
        # Step 3: Impute missing values
        imputed_data, imputation_log = self.impute_missing_values(project_data)
        
        if verbose and imputation_log:
            print(f"\n🔧 Imputed {len(imputation_log)} fields:")
            for field, method in imputation_log.items():
                print(f"   {field}: {method}")
        
        # Step 4: Return enriched data with quality metadata
        return {
            'status': 'SUCCESS',
            'quality': quality,
            'imputed_data': imputed_data,
            'imputation_log': imputation_log,
            'warnings': self._generate_warnings(quality, imputation_log)
        }
    
    def _generate_warnings(self, quality: dict, imputation_log: dict) -> List[str]:
        """Generate user-facing warnings about data quality"""
        warnings = []
        
        if quality['quality_level'] == 'LOW':
            warnings.append(f"⚠️  LOW data quality ({quality['completeness']:.0%} complete) - results may be unreliable")
        
        if quality['quality_level'] == 'MEDIUM':
            warnings.append(f"⚠️  MEDIUM data quality ({quality['completeness']:.0%} complete) - confidence reduced by {quality['confidence_penalty']:.0%}")
        
        if len(imputation_log) > 3:
            warnings.append(f"⚠️  {len(imputation_log)} fields imputed - verify data source completeness")
        
        if 'risk_score' in imputation_log:
            warnings.append(f"⚠️  Risk score was imputed using: {imputation_log['risk_score']}")
        
        return warnings
    
    def get_portfolio_data_quality_report(self, hours: int = 24) -> Dict:
        """
        Generate data quality report for entire portfolio
        
        Returns summary statistics:
        - Projects by quality level (HIGH/MEDIUM/LOW)
        - Most commonly missing fields
        - Projects requiring data improvement
        """
        # Get recent predictions
        recent = self.db.get_predictions(hours=hours)
        
        quality_counts = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'INSUFFICIENT': 0}
        missing_field_counts = {}
        projects_needing_improvement = []
        
        for pred in recent:
            project_data = {
                'project_id': pred.get('project_id'),
                'risk_score': pred.get('risk_score'),
                'cost_variance': pred.get('cost_variance'),
                'success_probability': pred.get('success_probability')
            }
            
            quality = self.assess_data_quality(project_data)
            
            if quality['can_analyze']:
                quality_counts[quality['quality_level']] += 1
            else:
                quality_counts['INSUFFICIENT'] += 1
            
            # Track missing fields
            for field in quality['missing_fields']:
                missing_field_counts[field] = missing_field_counts.get(field, 0) + 1
            
            # Flag projects needing improvement
            if quality['quality_level'] in ['LOW', 'MEDIUM'] or not quality['can_analyze']:
                projects_needing_improvement.append({
                    'project_id': pred.get('project_id'),
                    'quality_level': quality['quality_level'] if quality['can_analyze'] else 'INSUFFICIENT',
                    'completeness': quality['completeness'],
                    'missing_count': len(quality['missing_fields'])
                })
        
        # Sort by most commonly missing
        top_missing = sorted(missing_field_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Sort projects by worst quality
        projects_needing_improvement.sort(key=lambda x: x['completeness'])
        
        return {
            'total_projects': len(recent),
            'quality_distribution': quality_counts,
            'quality_percentage': {
                level: (count / len(recent) * 100) if len(recent) > 0 else 0
                for level, count in quality_counts.items()
            },
            'top_missing_fields': top_missing,
            'projects_needing_improvement': projects_needing_improvement[:10],  # Top 10 worst
            'overall_portfolio_health': self._calculate_portfolio_health(quality_counts, len(recent))
        }
    
    def _calculate_portfolio_health(self, quality_counts: dict, total: int) -> str:
        """Calculate overall portfolio data health"""
        if total == 0:
            return "NO_DATA"
        
        high_pct = quality_counts['HIGH'] / total
        insufficient_pct = quality_counts['INSUFFICIENT'] / total
        
        if high_pct >= 0.85:
            return "EXCELLENT"
        elif high_pct >= 0.70:
            return "GOOD"
        elif insufficient_pct > 0.20:
            return "POOR"
        else:
            return "FAIR"


# Demo and testing
if __name__ == "__main__":
    # Example usage
    db = PortfolioDB("portfolio_predictions.db")
    handler = MissingDataHandler(db)
    
    print("=" * 80)
    print("Missing Data Handler - Demo")
    print("=" * 80)
    
    # Test Case 1: Complete data
    print("\n📋 TEST 1: Complete Data")
    complete_data = {
        'project_id': 'PROJ-COMPLETE',
        'risk_score': 65,
        'cost_variance': 12.5,
        'success_probability': 0.82,
        'budget': 5000000,
        'team_size': 8,
        'duration_months': 12
    }
    result = handler.analyze_with_missing_data(complete_data, verbose=True)
    print(f"Status: {result['status']}")
    print(f"Quality: {result['quality']['quality_level']}")
    
    # Test Case 2: Partial data
    print("\n\n📋 TEST 2: Partial Data (Missing Optional Fields)")
    partial_data = {
        'project_id': 'PROJ-PARTIAL',
        'risk_score': 75,
        'cost_variance': 18.3
        # Missing: success_probability, budget, team_size, duration_months
    }
    result = handler.analyze_with_missing_data(partial_data, verbose=True)
    print(f"Status: {result['status']}")
    print(f"Quality: {result['quality']['quality_level']}")
    if result['warnings']:
        print("Warnings:")
        for warning in result['warnings']:
            print(f"  {warning}")
    
    # Test Case 3: Minimal data
    print("\n\n📋 TEST 3: Minimal Data (Only Required Field)")
    minimal_data = {
        'project_id': 'PROJ-MINIMAL',
        'risk_score': 50
        # Missing: everything else
    }
    result = handler.analyze_with_missing_data(minimal_data, verbose=True)
    print(f"Status: {result['status']}")
    if result['status'] == 'SUCCESS':
        print(f"Quality: {result['quality']['quality_level']}")
        if result.get('warnings'):
            print("Warnings:")
            for warning in result['warnings']:
                print(f"  {warning}")
    else:
        print(f"Message: {result['message']}")
    
    # Test Case 4: Insufficient data
    print("\n\n📋 TEST 4: Insufficient Data (Missing Required Field)")
    insufficient_data = {
        'project_id': 'PROJ-INSUFFICIENT',
        'cost_variance': 10.0
        # Missing: risk_score (required!)
    }
    result = handler.analyze_with_missing_data(insufficient_data, verbose=True)
    print(f"Status: {result['status']}")
    if result['status'] == 'INSUFFICIENT_DATA':
        print(f"Message: {result['message']}")
    
    # Portfolio Quality Report
    print("\n\n📊 PORTFOLIO DATA QUALITY REPORT")
    print("=" * 80)
    report = handler.get_portfolio_data_quality_report(hours=720)  # Last 30 days
    
    print(f"Total Projects: {report['total_projects']}")
    print(f"\nQuality Distribution:")
    for level, count in report['quality_distribution'].items():
        pct = report['quality_percentage'][level]
        print(f"  {level}: {count} ({pct:.1f}%)")
    
    print(f"\nOverall Portfolio Health: {report['overall_portfolio_health']}")
    
    if report['top_missing_fields']:
        print(f"\nMost Commonly Missing Fields:")
        for field, count in report['top_missing_fields']:
            print(f"  {field}: {count} projects")
    
    if report['projects_needing_improvement']:
        print(f"\nProjects Needing Data Improvement (Top 5):")
        for proj in report['projects_needing_improvement'][:5]:
            print(f"  {proj['project_id']}: {proj['quality_level']} ({proj['completeness']:.0%} complete)")
    
    print("\n" + "=" * 80)
