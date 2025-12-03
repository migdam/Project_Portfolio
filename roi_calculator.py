"""
ROI Calculator

Calculates Return on Investment with benefit quantification,
cost-benefit analysis, payback period, NPV, and risk-adjusted ROI.
"""

import numpy as np
from typing import Dict, List

class ROICalculator:
    """
    Calculates comprehensive ROI metrics for project valuation
    """
    
    def __init__(self, discount_rate: float = 0.10):
        """
        Initialize ROI calculator
        
        Args:
            discount_rate: Annual discount rate for NPV (default 10%)
        """
        self.discount_rate = discount_rate
    
    def calculate_roi(self, project_data: dict) -> Dict:
        """
        Calculate comprehensive ROI metrics
        
        Args:
            project_data: Project information including:
                - total_cost: Total project cost
                - cost_variance: Predicted cost overrun %
                - expected_benefits: Dict of benefit types and amounts
                - project_duration_years: Duration for benefit realization
                - risk_score: Risk score 0-100
                
        Returns:
            Dict with ROI metrics and financial analysis
        """
        # Extract project data
        base_cost = project_data.get('total_cost', 1000000)
        cost_variance_pct = project_data.get('cost_variance', 0)
        benefits = project_data.get('expected_benefits', {})
        duration = project_data.get('project_duration_years', 3)
        risk_score = project_data.get('risk_score', 50)
        
        # Calculate actual cost with overrun
        cost_overrun = base_cost * (cost_variance_pct / 100)
        actual_cost = base_cost + cost_overrun
        
        # Quantify benefits
        benefit_summary = self._quantify_benefits(benefits, duration)
        total_benefits = benefit_summary['total_annual_benefit'] * duration
        
        # Calculate basic ROI
        basic_roi = ((total_benefits - actual_cost) / actual_cost) * 100 if actual_cost > 0 else 0
        
        # Calculate risk-adjusted ROI
        risk_adjustment = self._calculate_risk_adjustment(risk_score)
        risk_adjusted_roi = basic_roi * risk_adjustment
        
        # Calculate payback period
        payback_period = self._calculate_payback_period(
            actual_cost,
            benefit_summary['total_annual_benefit']
        )
        
        # Calculate NPV
        npv = self._calculate_npv(
            actual_cost,
            benefit_summary['total_annual_benefit'],
            duration
        )
        
        # Financial viability assessment
        viability = self._assess_financial_viability(
            basic_roi,
            risk_adjusted_roi,
            payback_period,
            npv
        )
        
        return {
            'cost_analysis': {
                'base_cost': base_cost,
                'cost_overrun': cost_overrun,
                'actual_cost': actual_cost,
                'cost_variance_pct': cost_variance_pct
            },
            'benefit_analysis': benefit_summary,
            'roi_metrics': {
                'basic_roi_pct': basic_roi,
                'risk_adjusted_roi_pct': risk_adjusted_roi,
                'risk_adjustment_factor': risk_adjustment,
                'payback_period_years': payback_period,
                'npv': npv,
                'benefit_cost_ratio': total_benefits / actual_cost if actual_cost > 0 else 0
            },
            'financial_viability': viability,
            'recommendations': self._generate_financial_recommendations(
                basic_roi, risk_adjusted_roi, payback_period, npv, viability
            )
        }
    
    def _quantify_benefits(self, benefits: dict, duration: int) -> Dict:
        """Quantify and categorize benefits"""
        
        # Revenue benefits
        annual_revenue = benefits.get('annual_revenue_increase', 0)
        
        # Cost savings
        annual_savings = benefits.get('annual_cost_savings', 0)
        efficiency_pct = benefits.get('efficiency_improvement_pct', 0)
        efficiency_value = benefits.get('efficiency_base_cost', 0) * (efficiency_pct / 100)
        
        # Productivity benefits
        automation_hours = benefits.get('automation_hours', 0)
        hourly_rate = benefits.get('hourly_rate', 75)  # Default $75/hr
        productivity_value = automation_hours * hourly_rate
        
        # Risk reduction benefits
        risk_reduction_value = benefits.get('risk_mitigation_value', 0)
        
        # Strategic/intangible benefits (estimated)
        strategic_value = benefits.get('strategic_value_estimate', 0)
        
        total_annual = (
            annual_revenue +
            annual_savings +
            efficiency_value +
            productivity_value +
            risk_reduction_value / duration +  # Amortize one-time benefits
            strategic_value / duration
        )
        
        return {
            'total_annual_benefit': total_annual,
            'breakdown': {
                'revenue_increase': annual_revenue,
                'cost_savings': annual_savings,
                'efficiency_gains': efficiency_value,
                'productivity_gains': productivity_value,
                'risk_reduction': risk_reduction_value / duration,
                'strategic_value': strategic_value / duration
            },
            'total_lifetime_benefit': total_annual * duration
        }
    
    def _calculate_risk_adjustment(self, risk_score: float) -> float:
        """
        Calculate risk adjustment factor
        
        Higher risk = lower adjustment factor
        Risk 0 → 1.0 (no adjustment)
        Risk 50 → 0.85
        Risk 100 → 0.5
        """
        return 1.0 - (risk_score / 200)  # Max 50% reduction
    
    def _calculate_payback_period(self, cost: float, annual_benefit: float) -> float:
        """Calculate payback period in years"""
        if annual_benefit <= 0:
            return float('inf')
        return cost / annual_benefit
    
    def _calculate_npv(self, cost: float, annual_benefit: float, years: int) -> float:
        """Calculate Net Present Value"""
        # Initial investment (negative cash flow)
        npv = -cost
        
        # Add discounted benefits
        for year in range(1, years + 1):
            discounted_benefit = annual_benefit / ((1 + self.discount_rate) ** year)
            npv += discounted_benefit
        
        return npv
    
    def _assess_financial_viability(
        self,
        basic_roi: float,
        risk_adjusted_roi: float,
        payback: float,
        npv: float
    ) -> Dict:
        """Assess overall financial viability"""
        
        # Score each dimension
        roi_score = self._score_roi(risk_adjusted_roi)
        payback_score = self._score_payback(payback)
        npv_score = self._score_npv(npv)
        
        # Overall score (weighted average)
        overall_score = (
            roi_score * 0.4 +
            payback_score * 0.3 +
            npv_score * 0.3
        )
        
        # Determine viability level
        if overall_score >= 80:
            level = "EXCELLENT"
        elif overall_score >= 60:
            level = "GOOD"
        elif overall_score >= 40:
            level = "FAIR"
        else:
            level = "POOR"
        
        return {
            'overall_score': overall_score,
            'viability_level': level,
            'component_scores': {
                'roi_score': roi_score,
                'payback_score': payback_score,
                'npv_score': npv_score
            },
            'meets_threshold': overall_score >= 60
        }
    
    def _score_roi(self, roi: float) -> float:
        """Score ROI (0-100)"""
        if roi >= 100:
            return 100.0
        elif roi >= 50:
            return 90.0
        elif roi >= 25:
            return 70.0
        elif roi >= 10:
            return 50.0
        elif roi >= 0:
            return 30.0
        else:
            return 0.0
    
    def _score_payback(self, payback: float) -> float:
        """Score payback period (0-100)"""
        if payback <= 1:
            return 100.0
        elif payback <= 2:
            return 80.0
        elif payback <= 3:
            return 60.0
        elif payback <= 5:
            return 40.0
        else:
            return 20.0
    
    def _score_npv(self, npv: float) -> float:
        """Score NPV (0-100)"""
        if npv >= 5000000:
            return 100.0
        elif npv >= 1000000:
            return 80.0
        elif npv >= 500000:
            return 60.0
        elif npv >= 0:
            return 40.0
        else:
            return 20.0
    
    def _generate_financial_recommendations(
        self,
        basic_roi: float,
        risk_adjusted_roi: float,
        payback: float,
        npv: float,
        viability: Dict
    ) -> List[str]:
        """Generate financial recommendations"""
        recommendations = []
        
        level = viability['viability_level']
        
        if level == "EXCELLENT":
            recommendations.append("✅ Excellent financial case - high priority for funding")
        elif level == "GOOD":
            recommendations.append("✅ Strong financial case - recommend approval")
        elif level == "FAIR":
            recommendations.append("⚠️  Marginal financial case - consider benefit enhancement")
        else:
            recommendations.append("❌ Weak financial case - requires justification or redesign")
        
        # Specific metric recommendations
        if risk_adjusted_roi < 10:
            recommendations.append("⚠️  Low ROI - investigate benefit opportunities or cost reduction")
        
        if payback > 3:
            recommendations.append("⚠️  Long payback period - prioritize early benefit realization")
        
        if npv < 0:
            recommendations.append("❌ Negative NPV - project destroys value at current discount rate")
        
        if basic_roi > 0 and risk_adjusted_roi < 0:
            recommendations.append("⚠️  High risk impact - implement risk mitigation before proceeding")
        
        return recommendations


# Demo and testing
if __name__ == "__main__":
    print("=" * 80)
    print("ROI Calculator - Demo")
    print("=" * 80)
    
    calculator = ROICalculator(discount_rate=0.10)
    
    # Test Case 1: High ROI Digital Project
    print("\n📋 TEST 1: High ROI Digital Transformation Project")
    high_roi_project = {
        'project_id': 'PROJ-HIGH-ROI',
        'total_cost': 2000000,
        'cost_variance': 10,  # 10% overrun
        'expected_benefits': {
            'annual_revenue_increase': 1500000,
            'annual_cost_savings': 500000,
            'automation_hours': 5000,
            'hourly_rate': 100,
            'strategic_value_estimate': 300000
        },
        'project_duration_years': 3,
        'risk_score': 40
    }
    
    result = calculator.calculate_roi(high_roi_project)
    print(f"\n💰 Cost Analysis:")
    print(f"   Base Cost: ${result['cost_analysis']['base_cost']:,.0f}")
    print(f"   Cost Overrun: ${result['cost_analysis']['cost_overrun']:,.0f} ({result['cost_analysis']['cost_variance_pct']:.0f}%)")
    print(f"   Actual Cost: ${result['cost_analysis']['actual_cost']:,.0f}")
    
    print(f"\n📈 Benefit Analysis:")
    print(f"   Annual Benefit: ${result['benefit_analysis']['total_annual_benefit']:,.0f}")
    print(f"   Lifetime Benefit: ${result['benefit_analysis']['total_lifetime_benefit']:,.0f}")
    
    print(f"\n📊 ROI Metrics:")
    metrics = result['roi_metrics']
    print(f"   Basic ROI: {metrics['basic_roi_pct']:.1f}%")
    print(f"   Risk-Adjusted ROI: {metrics['risk_adjusted_roi_pct']:.1f}%")
    print(f"   Payback Period: {metrics['payback_period_years']:.1f} years")
    print(f"   NPV: ${metrics['npv']:,.0f}")
    print(f"   Benefit/Cost Ratio: {metrics['benefit_cost_ratio']:.2f}x")
    
    viability = result['financial_viability']
    print(f"\n✅ Financial Viability: {viability['viability_level']} ({viability['overall_score']:.0f}/100)")
    print(f"\nRecommendations:")
    for rec in result['recommendations']:
        print(f"   {rec}")
    
    # Test Case 2: Marginal ROI Project
    print("\n\n📋 TEST 2: Marginal ROI Cost Reduction Project")
    marginal_project = {
        'project_id': 'PROJ-MARGINAL',
        'total_cost': 1500000,
        'cost_variance': 20,
        'expected_benefits': {
            'annual_cost_savings': 400000,
            'efficiency_improvement_pct': 15,
            'efficiency_base_cost': 1000000
        },
        'project_duration_years': 3,
        'risk_score': 65
    }
    
    result = calculator.calculate_roi(marginal_project)
    metrics = result['roi_metrics']
    viability = result['financial_viability']
    
    print(f"   Actual Cost: ${result['cost_analysis']['actual_cost']:,.0f}")
    print(f"   Annual Benefit: ${result['benefit_analysis']['total_annual_benefit']:,.0f}")
    print(f"   Basic ROI: {metrics['basic_roi_pct']:.1f}%")
    print(f"   Risk-Adjusted ROI: {metrics['risk_adjusted_roi_pct']:.1f}%")
    print(f"   Payback Period: {metrics['payback_period_years']:.1f} years")
    print(f"   Financial Viability: {viability['viability_level']} ({viability['overall_score']:.0f}/100)")
    print(f"\nRecommendations:")
    for rec in result['recommendations']:
        print(f"   {rec}")
    
    # Test Case 3: Poor ROI Project
    print("\n\n📋 TEST 3: Poor ROI Maintenance Project")
    poor_project = {
        'project_id': 'PROJ-POOR',
        'total_cost': 1000000,
        'cost_variance': 25,
        'expected_benefits': {
            'annual_cost_savings': 150000,
            'risk_mitigation_value': 100000
        },
        'project_duration_years': 3,
        'risk_score': 80
    }
    
    result = calculator.calculate_roi(poor_project)
    metrics = result['roi_metrics']
    viability = result['financial_viability']
    
    print(f"   Actual Cost: ${result['cost_analysis']['actual_cost']:,.0f}")
    print(f"   Annual Benefit: ${result['benefit_analysis']['total_annual_benefit']:,.0f}")
    print(f"   Basic ROI: {metrics['basic_roi_pct']:.1f}%")
    print(f"   Risk-Adjusted ROI: {metrics['risk_adjusted_roi_pct']:.1f}%")
    print(f"   NPV: ${metrics['npv']:,.0f}")
    print(f"   Financial Viability: {viability['viability_level']} ({viability['overall_score']:.0f}/100)")
    print(f"\nRecommendations:")
    for rec in result['recommendations']:
        print(f"   {rec}")
    
    print("\n" + "=" * 80)
