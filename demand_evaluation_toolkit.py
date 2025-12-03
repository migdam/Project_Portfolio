#!/usr/bin/env python3
"""
Demand Evaluation Toolkit - Integrated AI-Powered Demand Evaluation

Combines all Portfolio ML components into a unified demand evaluation pipeline:
- ML-based automatic classification
- Strategic alignment scoring (GenAI)
- Financial viability analysis
- Risk & feasibility assessment
- Quality validation
- Priority scoring & routing

Author: Portfolio ML
Version: 1.0.0
"""

from typing import Dict, Optional, List
from demand_classifier import DemandClassifier
from strategic_alignment import StrategicAlignmentScorer
from roi_calculator import ROICalculator
from missing_data_handler import MissingDataHandler
from database import PortfolioDB
from demand_optimizer import DemandOptimizer


class DemandEvaluationToolkit:
    """
    Integrated toolkit for AI-powered demand evaluation
    
    Provides end-to-end automation for evaluating project ideas/demands:
    1. Automatic classification from text
    2. Quality validation
    3. Strategic alignment scoring
    4. Financial viability analysis
    5. Risk assessment
    6. Priority scoring
    7. Routing decision
    """
    
    def __init__(self, db_path: str = "portfolio_predictions.db"):
        """
        Initialize the demand evaluation toolkit
        
        Args:
            db_path: Path to SQLite database for historical data
        """
        # Initialize all components
        self.classifier = DemandClassifier()
        self.alignment_scorer = StrategicAlignmentScorer()
        self.roi_calculator = ROICalculator(discount_rate=0.10)
        
        self.db = PortfolioDB(db_path)
        self.quality_handler = MissingDataHandler(self.db)
        self.optimizer = DemandOptimizer()
        
        # Routing thresholds (configurable)
        self.thresholds = {
            'min_completeness': 0.30,  # Minimum data completeness
            'min_alignment': 30,  # Minimum strategic alignment score
            'min_roi': -50,  # Minimum acceptable ROI %
            'max_risk': 85,  # Maximum acceptable risk score
            'high_priority': 75,  # High priority threshold
            'medium_priority': 50  # Medium priority threshold
        }
    
    def evaluate_demand(self, idea_data: Dict, auto_classify: bool = False) -> Dict:
        """
        Complete demand evaluation pipeline
        
        Args:
            idea_data: Dictionary with idea information
                Required: project_id, risk_score
                Optional: project_type, description, title, etc.
            auto_classify: If True, automatically classify from description
            
        Returns:
            Dictionary with evaluation results and routing decision
        """
        result = {
            'project_id': idea_data.get('project_id', 'UNKNOWN'),
            'status': 'IN_PROGRESS',
            'routing': None,
            'priority_score': 0,
            'priority_tier': None,
            'steps': {}
        }
        
        # Step 1: Auto-classification (if requested)
        if auto_classify and 'description' in idea_data:
            classification = self._classify_idea(idea_data)
            result['steps']['classification'] = classification
            
            # Enrich idea_data with classification
            if classification['status'] == 'SUCCESS':
                idea_data['project_type'] = classification['category']
                idea_data['auto_classified'] = True
                
                # Map complexity to fields
                if classification['complexity'] == 'High':
                    idea_data['innovation_level'] = 'High'
                elif classification['complexity'] == 'Low':
                    idea_data['innovation_level'] = 'Low'
        
        # Step 2: Quality Validation
        quality_result = self._validate_quality(idea_data)
        result['steps']['quality'] = quality_result
        
        if quality_result['routing'] != 'PASS':
            result['routing'] = quality_result['routing']
            result['reason'] = quality_result['reason']
            result['status'] = 'REJECTED'
            return result
        
        # Step 3: Strategic Alignment
        alignment_result = self._evaluate_alignment(idea_data)
        result['steps']['alignment'] = alignment_result
        
        if alignment_result['routing'] != 'PASS':
            result['routing'] = alignment_result['routing']
            result['reason'] = alignment_result['reason']
            result['status'] = 'REJECTED'
            return result
        
        # Step 4: Financial Viability
        financial_result = self._evaluate_financial_viability(idea_data)
        result['steps']['financial'] = financial_result
        
        if financial_result['routing'] != 'PASS':
            result['routing'] = financial_result['routing']
            result['reason'] = financial_result['reason']
            result['status'] = 'REJECTED'
            return result
        
        # Step 5: Risk Assessment
        risk_result = self._assess_risk(idea_data)
        result['steps']['risk'] = risk_result
        
        if risk_result['routing'] != 'PASS':
            result['routing'] = risk_result['routing']
            result['reason'] = risk_result['reason']
            result['status'] = 'ESCALATED'
            return result
        
        # Step 6: Priority Scoring
        priority_result = self._calculate_priority(
            quality_result,
            alignment_result,
            financial_result,
            risk_result
        )
        result['steps']['priority'] = priority_result
        result['priority_score'] = priority_result['priority_score']
        result['priority_tier'] = priority_result['priority_tier']
        
        # Step 7: Final Routing
        result['routing'] = 'APPROVED'
        result['status'] = 'APPROVED'
        result['confidence'] = quality_result['completeness']
        
        # Collect recommendations
        recommendations = []
        if alignment_result.get('recommendations'):
            recommendations.extend(alignment_result['recommendations'])
        if risk_result.get('recommendations'):
            recommendations.extend(risk_result['recommendations'])
        result['recommendations'] = recommendations
        
        return result
    
    def _classify_idea(self, idea_data: Dict) -> Dict:
        """Step 1: Classify idea from text description"""
        description = idea_data.get('description', '')
        title = idea_data.get('title', '')
        
        if not description and not title:
            return {
                'status': 'SKIPPED',
                'reason': 'No description or title provided'
            }
        
        classification = self.classifier.classify_idea(description, title)
        
        return {
            'status': 'SUCCESS',
            'category': classification['category'],
            'sub_type': classification['sub_type'],
            'complexity': classification['complexity'],
            'confidence': classification['confidence'],
            'keywords': classification['keywords']
        }
    
    def _validate_quality(self, idea_data: Dict) -> Dict:
        """Step 2: Validate data quality"""
        quality = self.quality_handler.assess_data_quality(idea_data)
        
        if quality['quality_level'] == 'INSUFFICIENT':
            return {
                'routing': 'RETURN_FOR_COMPLETION',
                'reason': 'Incomplete submission - below minimum threshold',
                'completeness': quality['completeness'],
                'quality_level': quality['quality_level'],
                'missing_required': quality['missing_required'],
                'missing_optional': quality['missing_optional']
            }
        
        return {
            'routing': 'PASS',
            'completeness': quality['completeness'],
            'quality_level': quality['quality_level'],
            'confidence_penalty': quality['confidence_penalty']
        }
    
    def _evaluate_alignment(self, idea_data: Dict) -> Dict:
        """Step 3: Evaluate strategic alignment"""
        alignment = self.alignment_scorer.score_project(idea_data)
        
        if alignment['alignment_score'] < self.thresholds['min_alignment']:
            return {
                'routing': 'REJECT',
                'reason': f"Poor strategic fit (score: {alignment['alignment_score']:.0f}/100)",
                'alignment_score': alignment['alignment_score'],
                'alignment_level': alignment['alignment_level'],
                'weak_pillars': alignment['weak_pillars']
            }
        
        return {
            'routing': 'PASS',
            'alignment_score': alignment['alignment_score'],
            'alignment_level': alignment['alignment_level'],
            'strong_pillars': alignment['strong_pillars'],
            'weak_pillars': alignment['weak_pillars'],
            'recommendations': alignment['recommendations']
        }
    
    def _evaluate_financial_viability(self, idea_data: Dict) -> Dict:
        """Step 4: Evaluate financial viability"""
        roi_result = self.roi_calculator.calculate_roi(idea_data)
        metrics = roi_result['roi_metrics']
        viability = roi_result['financial_viability']
        
        # Check minimum ROI threshold
        if metrics['risk_adjusted_roi_pct'] < self.thresholds['min_roi']:
            return {
                'routing': 'REJECT',
                'reason': f"Financially unviable (ROI: {metrics['risk_adjusted_roi_pct']:.1f}%)",
                'roi': metrics['risk_adjusted_roi_pct'],
                'payback_period': metrics['payback_period_years'],
                'npv': metrics['npv_dollars'],
                'viability_level': viability['viability_level']
            }
        
        return {
            'routing': 'PASS',
            'roi': metrics['risk_adjusted_roi_pct'],
            'payback_period': metrics['payback_period_years'],
            'npv': metrics['npv_dollars'],
            'viability_level': viability['viability_level'],
            'viability_score': viability['viability_score']
        }
    
    def _assess_risk(self, idea_data: Dict) -> Dict:
        """Step 5: Assess risk and feasibility"""
        # Use imputed data for risk assessment
        imputed_result = self.quality_handler.analyze_with_missing_data(idea_data)
        
        if imputed_result['status'] != 'SUCCESS':
            return {
                'routing': 'RETURN_FOR_COMPLETION',
                'reason': 'Insufficient data for risk assessment',
                'risk_score': 0
            }
        
        imputed_data = imputed_result['imputed_data']
        risk_score = imputed_data['risk_score']
        
        # Determine risk level
        if risk_score > self.thresholds['max_risk']:
            risk_level = 'CRITICAL'
        elif risk_score > 60:
            risk_level = 'HIGH'
        elif risk_score > 40:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        # Escalate if critical risk
        if risk_score > self.thresholds['max_risk']:
            return {
                'routing': 'ESCALATE_HIGH_RISK',
                'reason': f"Critical risk level (score: {risk_score}/100)",
                'risk_score': risk_score,
                'risk_level': risk_level,
                'recommendations': [
                    f"Risk score {risk_score} exceeds threshold {self.thresholds['max_risk']}",
                    "Requires executive review and mitigation plan",
                    "Consider breaking into smaller, lower-risk phases"
                ]
            }
        
        return {
            'routing': 'PASS',
            'risk_score': risk_score,
            'risk_level': risk_level,
            'recommendations': []
        }
    
    def _calculate_priority(self, quality_result: Dict, alignment_result: Dict,
                           financial_result: Dict, risk_result: Dict) -> Dict:
        """Step 6: Calculate priority score"""
        # Weighted priority calculation
        # Strategic Alignment: 35%
        # Risk-Adjusted Success: 25%
        # Financial Viability: 40%
        
        alignment_score = alignment_result['alignment_score']
        risk_score = risk_result['risk_score']
        viability_score = financial_result.get('viability_score', 50)
        
        # Risk-adjusted success score (inverse of risk)
        success_score = 100 - risk_score
        
        # Calculate weighted priority
        priority_score = (
            alignment_score * 0.35 +
            success_score * 0.25 +
            min(viability_score, 100) * 0.40
        )
        
        # Determine priority tier
        if priority_score >= self.thresholds['high_priority']:
            priority_tier = 'HIGH'
        elif priority_score >= self.thresholds['medium_priority']:
            priority_tier = 'MEDIUM'
        else:
            priority_tier = 'LOW'
        
        return {
            'priority_score': priority_score,
            'priority_tier': priority_tier,
            'components': {
                'strategic_alignment': alignment_score,
                'risk_adjusted_success': success_score,
                'financial_viability': viability_score
            },
            'weights': {
                'strategic_alignment': 0.35,
                'risk_adjusted_success': 0.25,
                'financial_viability': 0.40
            }
        }
    
    def evaluate_batch(self, ideas: list, auto_classify: bool = False) -> list:
        """
        Evaluate multiple ideas in batch
        
        Args:
            ideas: List of idea dictionaries
            auto_classify: If True, automatically classify from descriptions
            
        Returns:
            List of evaluation results
        """
        results = []
        for idea in ideas:
            result = self.evaluate_demand(idea, auto_classify=auto_classify)
            results.append(result)
        
        return results
    
    def get_summary(self, results: list) -> Dict:
        """
        Generate summary statistics for batch evaluation
        
        Args:
            results: List of evaluation results
            
        Returns:
            Summary statistics
        """
        total = len(results)
        
        # Count by routing decision
        routing_counts = {}
        for result in results:
            routing = result['routing']
            routing_counts[routing] = routing_counts.get(routing, 0) + 1
        
        # Count by priority tier (for approved ideas)
        priority_counts = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        approved_results = [r for r in results if r['routing'] == 'APPROVED']
        for result in approved_results:
            tier = result.get('priority_tier')
            if tier in priority_counts:
                priority_counts[tier] += 1
        
        # Average scores
        avg_priority = sum(r['priority_score'] for r in approved_results) / len(approved_results) if approved_results else 0
        avg_alignment = sum(
            r['steps']['alignment']['alignment_score'] 
            for r in results 
            if 'alignment' in r['steps'] and 'alignment_score' in r['steps']['alignment']
        ) / total if total > 0 else 0
        
        return {
            'total_evaluated': total,
            'routing_distribution': routing_counts,
            'priority_distribution': priority_counts,
            'approved_count': routing_counts.get('APPROVED', 0),
            'rejected_count': routing_counts.get('REJECT', 0),
            'returned_count': routing_counts.get('RETURN_FOR_COMPLETION', 0),
            'escalated_count': routing_counts.get('ESCALATE_HIGH_RISK', 0),
            'approval_rate': routing_counts.get('APPROVED', 0) / total if total > 0 else 0,
            'avg_priority_score': avg_priority,
            'avg_alignment_score': avg_alignment
        }
    
    def optimize_portfolio(
        self,
        approved_demands: List[Dict],
        constraints: Dict,
        objective: str = 'balanced',
        weights: Optional[Dict] = None
    ) -> Dict:
        """
        Optimize portfolio selection from approved demands using Linear Programming
        
        Args:
            approved_demands: List of approved demand evaluation results
            constraints: Resource constraints dictionary:
                - total_budget: Maximum budget ($)
                - max_concurrent_projects: Max number of projects
                - max_avg_risk: Maximum average risk score
                - resource_capacity: Dict of {skill: FTE_capacity}
            objective: Optimization objective
                - 'maximize_npv': Maximize total NPV
                - 'maximize_strategic': Maximize strategic alignment
                - 'balanced': Weighted combination (default)
            weights: Optional weights for balanced objective
                - npv_weight: Weight for NPV (default 0.6)
                - strategic_weight: Weight for strategic value (default 0.4)
        
        Returns:
            Optimization results with selected projects and metrics
        """
        return self.optimizer.optimize(
            approved_demands=approved_demands,
            constraints=constraints,
            objective=objective,
            weights=weights
        )


def main():
    """Demo: Evaluate sample demands"""
    print("=" * 80)
    print("DEMAND EVALUATION TOOLKIT - INTEGRATED AI-POWERED EVALUATION")
    print("=" * 80)
    
    toolkit = DemandEvaluationToolkit()
    
    # Test idea with auto-classification
    test_idea = {
        'project_id': 'IDEA-2024-001',
        'title': 'AI-Powered Customer Support Chatbot',
        'description': '''
            Implement AI-powered chatbot for customer service using machine learning.
            Expected to reduce support costs by 40% and improve response time from 2 hours to 5 minutes.
            Requires integration with existing CRM system and 6-month implementation timeline.
            Initial investment of $500K with expected annual savings of $1.2M.
        ''',
        'risk_score': 45,
        'total_cost': 500_000,
        'expected_benefits': {
            'annual_cost_savings': 1_200_000,
            'automation_hours': 10000
        },
        'project_duration_years': 2
    }
    
    print("\n" + "─" * 80)
    print(f"Evaluating: {test_idea['title']}")
    print("─" * 80)
    
    result = toolkit.evaluate_demand(test_idea, auto_classify=True)
    
    print(f"\n✅ EVALUATION COMPLETE")
    print(f"\nRouting Decision: {result['routing']}")
    print(f"Status: {result['status']}")
    
    if result['routing'] == 'APPROVED':
        print(f"Priority: {result['priority_tier']} ({result['priority_score']:.0f}/100)")
        print(f"Confidence: {result['confidence']:.1%}")
        
        print(f"\n📊 Evaluation Steps:")
        for step_name, step_data in result['steps'].items():
            print(f"\n  {step_name.upper()}:")
            if step_name == 'classification' and step_data.get('status') == 'SUCCESS':
                print(f"    Category: {step_data['category']}")
                print(f"    Sub-type: {step_data['sub_type']}")
                print(f"    Confidence: {step_data['confidence']:.1%}")
            elif step_name == 'alignment':
                print(f"    Score: {step_data['alignment_score']:.0f}/100")
                print(f"    Level: {step_data['alignment_level']}")
            elif step_name == 'financial':
                print(f"    ROI: {step_data['roi']:.1f}%")
                print(f"    Payback: {step_data['payback_period']:.1f} years")
                print(f"    Viability: {step_data['viability_level']}")
            elif step_name == 'risk':
                print(f"    Risk Score: {step_data['risk_score']}/100")
                print(f"    Risk Level: {step_data['risk_level']}")
    else:
        print(f"Reason: {result.get('reason', 'N/A')}")
    
    print(f"\n{'=' * 80}")
    print("Evaluation complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
