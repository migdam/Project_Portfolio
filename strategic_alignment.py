"""
Strategic Alignment Framework

Validates project alignment with organizational strategic goals.
Provides scoring across multiple strategic dimensions.
"""

from typing import Dict, List
from enum import Enum

class StrategicPillar(Enum):
    """Strategic focus areas for portfolio alignment"""
    DIGITAL_TRANSFORMATION = "digital_transformation"
    COST_REDUCTION = "cost_reduction"
    MARKET_EXPANSION = "market_expansion"
    INNOVATION = "innovation"
    RISK_MANAGEMENT = "risk_management"

class StrategicAlignmentScorer:
    """
    Assesses how well a project aligns with organizational strategy
    """
    
    def __init__(self, org_strategy: Dict[str, float] = None):
        """
        Initialize with organizational strategic weights
        
        Args:
            org_strategy: Dict mapping strategic pillars to weights (0-100)
                         If None, uses balanced defaults
        """
        self.org_strategy = org_strategy or self._default_strategy()
    
    def _default_strategy(self) -> Dict[str, float]:
        """Default balanced strategic weights"""
        return {
            StrategicPillar.DIGITAL_TRANSFORMATION.value: 30.0,
            StrategicPillar.COST_REDUCTION.value: 25.0,
            StrategicPillar.MARKET_EXPANSION.value: 20.0,
            StrategicPillar.INNOVATION.value: 15.0,
            StrategicPillar.RISK_MANAGEMENT.value: 10.0
        }
    
    def score_project(self, project_data: dict) -> Dict:
        """
        Score project alignment with strategic goals
        
        Args:
            project_data: Project information including:
                - project_type: str (e.g., "Digital", "Cost Optimization")
                - expected_benefits: dict
                - innovation_level: str ("High", "Medium", "Low")
                - market_impact: str ("High", "Medium", "Low")
                
        Returns:
            Dict with alignment scores and overall assessment
        """
        # Extract project characteristics
        project_type = project_data.get('project_type', 'Operational')
        benefits = project_data.get('expected_benefits', {})
        innovation = project_data.get('innovation_level', 'Low')
        market_impact = project_data.get('market_impact', 'Low')
        
        # Score each strategic pillar
        pillar_scores = {}
        
        # Digital Transformation
        pillar_scores[StrategicPillar.DIGITAL_TRANSFORMATION.value] = self._score_digital_transformation(
            project_type, benefits
        )
        
        # Cost Reduction
        pillar_scores[StrategicPillar.COST_REDUCTION.value] = self._score_cost_reduction(
            benefits
        )
        
        # Market Expansion
        pillar_scores[StrategicPillar.MARKET_EXPANSION.value] = self._score_market_expansion(
            market_impact, benefits
        )
        
        # Innovation
        pillar_scores[StrategicPillar.INNOVATION.value] = self._score_innovation(
            innovation, project_type
        )
        
        # Risk Management
        pillar_scores[StrategicPillar.RISK_MANAGEMENT.value] = self._score_risk_management(
            project_data
        )
        
        # Calculate weighted alignment score
        alignment_score = self._calculate_weighted_score(pillar_scores)
        
        # Determine alignment level
        alignment_level = self._get_alignment_level(alignment_score)
        
        return {
            'alignment_score': alignment_score,
            'alignment_level': alignment_level,
            'pillar_scores': pillar_scores,
            'strategic_fit': self._assess_strategic_fit(pillar_scores),
            'recommendations': self._generate_recommendations(pillar_scores, alignment_score)
        }
    
    def _score_digital_transformation(self, project_type: str, benefits: dict) -> float:
        """Score digital transformation alignment (0-100)"""
        score = 0.0
        
        digital_types = ['Digital', 'Technology', 'Automation', 'Cloud', 'AI/ML']
        if any(dt.lower() in project_type.lower() for dt in digital_types):
            score += 70.0
        
        if benefits.get('automation_hours', 0) > 0:
            score += 20.0
        
        if benefits.get('digital_capability', False):
            score += 10.0
        
        return min(score, 100.0)
    
    def _score_cost_reduction(self, benefits: dict) -> float:
        """Score cost reduction alignment (0-100)"""
        score = 0.0
        
        annual_savings = benefits.get('annual_cost_savings', 0)
        if annual_savings > 1000000:
            score += 100.0
        elif annual_savings > 500000:
            score += 80.0
        elif annual_savings > 100000:
            score += 60.0
        elif annual_savings > 0:
            score += 40.0
        
        efficiency_gain = benefits.get('efficiency_improvement_pct', 0)
        if efficiency_gain > 0:
            score += min(efficiency_gain, 30.0)
        
        return min(score, 100.0)
    
    def _score_market_expansion(self, market_impact: str, benefits: dict) -> float:
        """Score market expansion alignment (0-100)"""
        score = 0.0
        
        impact_scores = {'High': 80.0, 'Medium': 50.0, 'Low': 20.0}
        score += impact_scores.get(market_impact, 20.0)
        
        revenue_impact = benefits.get('annual_revenue_increase', 0)
        if revenue_impact > 5000000:
            score += 20.0
        elif revenue_impact > 1000000:
            score += 10.0
        
        return min(score, 100.0)
    
    def _score_innovation(self, innovation_level: str, project_type: str) -> float:
        """Score innovation alignment (0-100)"""
        score = 0.0
        
        innovation_scores = {'High': 90.0, 'Medium': 60.0, 'Low': 30.0}
        score += innovation_scores.get(innovation_level, 30.0)
        
        innovative_types = ['R&D', 'Innovation', 'Pilot', 'Experimental']
        if any(it.lower() in project_type.lower() for it in innovative_types):
            score += 10.0
        
        return min(score, 100.0)
    
    def _score_risk_management(self, project_data: dict) -> float:
        """Score risk management alignment (0-100)"""
        risk_score = project_data.get('risk_score', 50)
        
        # Lower risk = better risk management
        # Invert: risk_score 0 → 100, risk_score 100 → 0
        score = 100.0 - risk_score
        
        # Bonus for explicit risk mitigation
        if project_data.get('risk_mitigation_plan', False):
            score += 10.0
        
        return min(score, 100.0)
    
    def _calculate_weighted_score(self, pillar_scores: dict) -> float:
        """Calculate weighted alignment score"""
        total_score = 0.0
        total_weight = 0.0
        
        for pillar, weight in self.org_strategy.items():
            score = pillar_scores.get(pillar, 0)
            total_score += score * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _get_alignment_level(self, score: float) -> str:
        """Determine alignment level from score"""
        if score >= 80:
            return "EXCELLENT"
        elif score >= 60:
            return "GOOD"
        elif score >= 40:
            return "FAIR"
        else:
            return "POOR"
    
    def _assess_strategic_fit(self, pillar_scores: dict) -> Dict:
        """Assess which pillars are well-aligned"""
        return {
            'strong_pillars': [p for p, s in pillar_scores.items() if s >= 70],
            'weak_pillars': [p for p, s in pillar_scores.items() if s < 40],
            'balanced': len([s for s in pillar_scores.values() if 40 <= s < 70]) >= 3
        }
    
    def _generate_recommendations(self, pillar_scores: dict, overall_score: float) -> List[str]:
        """Generate strategic alignment recommendations"""
        recommendations = []
        
        if overall_score < 40:
            recommendations.append("❌ Low strategic alignment - reconsider project or redefine scope")
        elif overall_score < 60:
            recommendations.append("⚠️  Fair strategic alignment - strengthen value proposition")
        
        # Specific pillar recommendations
        for pillar, score in pillar_scores.items():
            if score < 30 and self.org_strategy.get(pillar, 0) > 20:
                pillar_name = pillar.replace('_', ' ').title()
                recommendations.append(f"⚠️  Weak {pillar_name} alignment - consider enhancing this dimension")
        
        if overall_score >= 80:
            recommendations.append("✅ Excellent strategic fit - high priority for approval")
        
        return recommendations


# Demo and testing
if __name__ == "__main__":
    print("=" * 80)
    print("Strategic Alignment Framework - Demo")
    print("=" * 80)
    
    scorer = StrategicAlignmentScorer()
    
    # Test Case 1: Digital Transformation Project
    print("\n📋 TEST 1: Digital Transformation Project")
    digital_project = {
        'project_id': 'PROJ-DIGITAL-001',
        'project_type': 'Digital Transformation',
        'expected_benefits': {
            'automation_hours': 5000,
            'digital_capability': True,
            'annual_cost_savings': 750000
        },
        'innovation_level': 'High',
        'market_impact': 'Medium',
        'risk_score': 45
    }
    
    result = scorer.score_project(digital_project)
    print(f"Alignment Score: {result['alignment_score']:.1f}/100")
    print(f"Alignment Level: {result['alignment_level']}")
    print(f"\nPillar Scores:")
    for pillar, score in result['pillar_scores'].items():
        print(f"  {pillar.replace('_', ' ').title():25s}: {score:.1f}")
    print(f"\nRecommendations:")
    for rec in result['recommendations']:
        print(f"  {rec}")
    
    # Test Case 2: Cost Reduction Project
    print("\n\n📋 TEST 2: Cost Reduction Project")
    cost_project = {
        'project_id': 'PROJ-COST-001',
        'project_type': 'Cost Optimization',
        'expected_benefits': {
            'annual_cost_savings': 1500000,
            'efficiency_improvement_pct': 25
        },
        'innovation_level': 'Low',
        'market_impact': 'Low',
        'risk_score': 30
    }
    
    result = scorer.score_project(cost_project)
    print(f"Alignment Score: {result['alignment_score']:.1f}/100")
    print(f"Alignment Level: {result['alignment_level']}")
    print(f"\nPillar Scores:")
    for pillar, score in result['pillar_scores'].items():
        print(f"  {pillar.replace('_', ' ').title():25s}: {score:.1f}")
    print(f"\nStrategic Fit:")
    fit = result['strategic_fit']
    print(f"  Strong Pillars: {', '.join([p.replace('_', ' ').title() for p in fit['strong_pillars']])}")
    if fit['weak_pillars']:
        print(f"  Weak Pillars: {', '.join([p.replace('_', ' ').title() for p in fit['weak_pillars']])}")
    print(f"\nRecommendations:")
    for rec in result['recommendations']:
        print(f"  {rec}")
    
    # Test Case 3: Poorly Aligned Project
    print("\n\n📋 TEST 3: Poorly Aligned Project")
    poor_project = {
        'project_id': 'PROJ-POOR-001',
        'project_type': 'Operational Maintenance',
        'expected_benefits': {
            'annual_cost_savings': 50000
        },
        'innovation_level': 'Low',
        'market_impact': 'Low',
        'risk_score': 75
    }
    
    result = scorer.score_project(poor_project)
    print(f"Alignment Score: {result['alignment_score']:.1f}/100")
    print(f"Alignment Level: {result['alignment_level']}")
    print(f"\nRecommendations:")
    for rec in result['recommendations']:
        print(f"  {rec}")
    
    print("\n" + "=" * 80)
