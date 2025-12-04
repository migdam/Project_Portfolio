#!/usr/bin/env python3
"""
Integrated Agent Orchestrator

Connects LangGraph deep agent to all portfolio intelligence features:
- Demand Evaluation
- Benefit Intelligence
- Sequencing Optimization
- Location Resource Optimization
- Risk & Cost Prediction

The agent acts as an intelligent coordinator that:
1. Analyzes incoming project ideas
2. Routes them through appropriate evaluation pipelines
3. Monitors benefit realization
4. Optimizes portfolio execution sequence
5. Assigns optimal locations
6. Provides autonomous recommendations

Author: Portfolio ML
Version: 1.0.0
"""

from typing import Dict, List, Optional
from langgraph_agent import PortfolioAgent
from demand_evaluation_toolkit import DemandEvaluationToolkit
from benefit_tracker import BenefitRealizationTracker
from benefit_trend_analyzer import BenefitTrendAnalyzer
from benefit_alert_system import BenefitAlertSystem
from sequencing_optimizer import SequencingOptimizer
from location_resource_optimizer import LocationResourceOptimizer
from datetime import datetime
import json


class IntegratedAgentOrchestrator:
    """
    Orchestrates all portfolio intelligence features through LangGraph agent
    
    The agent provides autonomous decision-making and coordination across:
    - Demand evaluation and routing
    - Benefit tracking and prediction
    - Dependency-based sequencing
    - Multi-site resource allocation
    - Risk and cost analysis
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        db_path: str = "data/benefit_tracking.db",
        use_llm: bool = True
    ):
        """Initialize integrated orchestrator with deep agent"""
        
        # Core agent
        self.agent = PortfolioAgent(api_key=api_key, use_llm=use_llm)
        
        # Feature modules
        self.demand_toolkit = DemandEvaluationToolkit()
        self.benefit_tracker = BenefitRealizationTracker(db_path=db_path)
        self.trend_analyzer = BenefitTrendAnalyzer(db_path=db_path)
        self.alert_system = BenefitAlertSystem(db_path=db_path)
        self.sequencing_optimizer = SequencingOptimizer()
        self.location_optimizer = LocationResourceOptimizer()
        
        self.use_llm = use_llm
    
    def autonomous_idea_evaluation(self, idea: Dict) -> Dict:
        """
        Agent-powered autonomous evaluation of new project idea
        
        Flow:
        1. Agent analyzes idea characteristics
        2. Routes through demand evaluation
        3. Provides intelligent routing decision
        4. Suggests optimizations
        
        Args:
            idea: Project idea dictionary
        
        Returns:
            Evaluation results with agent recommendations
        """
        print(f"🤖 Agent: Evaluating new idea '{idea.get('title', 'Untitled')}'")
        
        # Evaluate through demand toolkit
        evaluation = self.demand_toolkit.evaluate_demand(idea, auto_classify=True)
        
        # Agent analysis of evaluation
        agent_insights = {
            'evaluated_at': datetime.now().isoformat(),
            'routing_decision': evaluation['routing'],
            'priority_tier': evaluation['priority_tier'],
            'agent_recommendation': None
        }
        
        # Agent reasoning about routing
        if evaluation['routing'] == 'APPROVED':
            priority_score = evaluation['priority_score']
            if priority_score >= 80:
                agent_insights['agent_recommendation'] = {
                    'action': 'FAST_TRACK',
                    'reason': f'High priority score ({priority_score}/100) - expedite for immediate portfolio inclusion',
                    'confidence': 0.95
                }
            elif priority_score >= 60:
                agent_insights['agent_recommendation'] = {
                    'action': 'STANDARD_REVIEW',
                    'reason': 'Medium priority - include in next portfolio planning cycle',
                    'confidence': 0.85
                }
            else:
                agent_insights['agent_recommendation'] = {
                    'action': 'CONDITIONAL_APPROVAL',
                    'reason': 'Lower priority - approve if resources become available',
                    'confidence': 0.70
                }
        elif evaluation['routing'] == 'ESCALATE':
            agent_insights['agent_recommendation'] = {
                'action': 'HUMAN_REVIEW_REQUIRED',
                'reason': 'High risk or uncertainty detected - executive review needed',
                'confidence': 0.60
            }
        else:
            agent_insights['agent_recommendation'] = {
                'action': 'REJECT_WITH_FEEDBACK',
                'reason': f"Routing: {evaluation['routing']} - provide feedback to submitter",
                'confidence': 0.85
            }
        
        return {
            'evaluation': evaluation,
            'agent_insights': agent_insights
        }
    
    def autonomous_benefit_monitoring(self, project_id: str) -> Dict:
        """
        Agent-powered benefit monitoring and early warning
        
        Flow:
        1. Track benefit realization
        2. Detect trends and anomalies
        3. Generate predictive alerts
        4. Recommend interventions
        
        Args:
            project_id: Project to monitor
        
        Returns:
            Monitoring results with agent recommendations
        """
        print(f"🤖 Agent: Monitoring benefits for {project_id}")
        
        # Get benefit status
        variance = self.benefit_tracker.calculate_variance(project_id)
        
        # Trend analysis
        underperforming = self.trend_analyzer.detect_underperforming_categories(threshold_pct=85)
        
        # Predictive alerts
        warnings = self.alert_system.generate_early_warning(deviation_threshold=0.15)
        
        # Agent synthesis
        agent_synthesis = {
            'monitored_at': datetime.now().isoformat(),
            'project_id': project_id,
            'health_status': 'UNKNOWN',
            'agent_actions': []
        }
        
        # Determine health status
        if variance and variance.get('status') == 'SUCCESS':
            realization_rate = variance.get('realization_rate', 0)
            
            if realization_rate >= 90:
                agent_synthesis['health_status'] = 'HEALTHY'
                agent_synthesis['agent_actions'].append({
                    'action': 'CAPTURE_SUCCESS_PATTERNS',
                    'reason': f'High realization rate ({realization_rate:.1f}%) - document best practices'
                })
            elif realization_rate >= 70:
                agent_synthesis['health_status'] = 'AT_RISK'
                agent_synthesis['agent_actions'].append({
                    'action': 'MONITOR_CLOSELY',
                    'reason': f'Realization rate {realization_rate:.1f}% - increase monitoring frequency'
                })
            else:
                agent_synthesis['health_status'] = 'CRITICAL'
                agent_synthesis['agent_actions'].append({
                    'action': 'IMMEDIATE_INTERVENTION',
                    'reason': f'Low realization rate ({realization_rate:.1f}%) - root cause analysis required'
                })
        
        return {
            'variance': variance,
            'underperforming': underperforming,
            'warnings': warnings,
            'agent_synthesis': agent_synthesis
        }
    
    def autonomous_portfolio_sequencing(
        self,
        projects: List[Dict],
        max_parallel: int = 5,
        resource_constraints: Optional[Dict] = None
    ) -> Dict:
        """
        Agent-powered portfolio sequencing optimization
        
        Flow:
        1. Analyze project dependencies
        2. Calculate critical path
        3. Optimize execution sequence
        4. Provide intelligent scheduling recommendations
        
        Args:
            projects: List of project dictionaries
            max_parallel: Maximum concurrent projects
            resource_constraints: Resource capacity limits
        
        Returns:
            Sequencing results with agent recommendations
        """
        print(f"🤖 Agent: Optimizing execution sequence for {len(projects)} projects")
        
        # Add projects to sequencing optimizer
        for proj in projects:
            self.sequencing_optimizer.add_project(
                project_id=proj['project_id'],
                duration_months=proj.get('duration_months', 6),
                priority_score=proj.get('priority_score', 50),
                dependencies=proj.get('dependencies', []),
                resource_requirements=proj.get('resource_requirements', {}),
                strategic_value=proj.get('strategic_value', 0),
                npv=proj.get('npv', 0)
            )
        
        # Optimize sequence
        result = self.sequencing_optimizer.optimize_sequence(
            max_parallel_projects=max_parallel,
            resource_constraints=resource_constraints
        )
        
        # Agent analysis
        agent_analysis = {
            'analyzed_at': datetime.now().isoformat(),
            'optimization_success': result['status'] == 'SUCCESS',
            'agent_recommendations': []
        }
        
        if result['status'] == 'SUCCESS':
            # Analyze critical path
            critical_path_length = len(result.get('critical_path', []))
            total_duration = result.get('total_duration_months', 0)
            
            agent_analysis['agent_recommendations'].append({
                'type': 'TIMELINE_INSIGHT',
                'insight': f'Critical path contains {critical_path_length} projects over {total_duration} months',
                'recommendation': 'Focus management attention on critical path projects to minimize delays'
            })
            
            # Resource utilization analysis
            resource_util = result.get('resource_utilization', {}).get('summary', {})
            for res_type, stats in resource_util.items():
                if stats.get('peak_utilization_pct', 0) > 90:
                    agent_analysis['agent_recommendations'].append({
                        'type': 'RESOURCE_WARNING',
                        'resource': res_type,
                        'utilization': stats['peak_utilization_pct'],
                        'recommendation': f'{res_type} at {stats["peak_utilization_pct"]:.0f}% - consider resource augmentation'
                    })
        
        return {
            'sequencing_result': result,
            'agent_analysis': agent_analysis
        }
    
    def autonomous_location_assignment(
        self,
        projects: List[Dict],
        location_resources: Dict[str, Dict[str, float]],
        objective: str = 'maximize_value'
    ) -> Dict:
        """
        Agent-powered multi-site location assignment
        
        Flow:
        1. Define location resource pools
        2. Assign projects to optimal locations
        3. Analyze cost-benefit tradeoffs
        4. Provide site-specific recommendations
        
        Args:
            projects: List of project dictionaries
            location_resources: {location: {resource_type: capacity}}
            objective: Optimization objective
        
        Returns:
            Location assignment with agent recommendations
        """
        print(f"🤖 Agent: Assigning {len(projects)} projects to optimal locations")
        
        # Setup location resources
        for location, resources in location_resources.items():
            for res_type, capacity in resources.items():
                cost_mult = {'US': 1.2, 'EU': 1.0, 'APAC': 0.7}.get(location, 1.0)
                self.location_optimizer.add_location_resource(
                    location=location,
                    resource_type=res_type,
                    capacity=capacity,
                    cost_multiplier=cost_mult
                )
        
        # Add projects
        for proj in projects:
            self.location_optimizer.add_project(
                project_id=proj['project_id'],
                allowed_locations=proj.get('allowed_locations', ['US', 'EU', 'APAC']),
                resource_requirements=proj.get('resource_requirements', {}),
                priority_score=proj.get('priority_score', 50),
                strategic_value=proj.get('strategic_value', 0),
                npv=proj.get('npv', 0),
                preferred_location=proj.get('preferred_location')
            )
        
        # Optimize
        result = self.location_optimizer.optimize(
            objective=objective,
            prefer_local_resources=True
        )
        
        # Agent analysis
        agent_analysis = {
            'analyzed_at': datetime.now().isoformat(),
            'optimization_success': result['status'] == 'SUCCESS',
            'agent_recommendations': []
        }
        
        if result['status'] == 'SUCCESS':
            # Analyze location distribution
            projects_by_location = result.get('projects_by_location', {})
            
            for location, proj_list in projects_by_location.items():
                utilization = result.get('location_utilization', {}).get(location, {})
                
                # Check for high utilization
                avg_util = sum(
                    res['utilization_pct'] 
                    for res in utilization.values()
                ) / len(utilization) if utilization else 0
                
                agent_analysis['agent_recommendations'].append({
                    'type': 'LOCATION_INSIGHT',
                    'location': location,
                    'projects_assigned': len(proj_list),
                    'avg_utilization': avg_util,
                    'recommendation': f'{location}: {len(proj_list)} projects at {avg_util:.0f}% avg utilization'
                })
        
        return {
            'location_result': result,
            'agent_analysis': agent_analysis
        }
    
    def full_portfolio_orchestration(
        self,
        new_ideas: List[Dict],
        active_projects: List[Dict],
        location_resources: Dict[str, Dict[str, float]],
        resource_constraints: Optional[Dict] = None
    ) -> Dict:
        """
        Complete autonomous portfolio orchestration
        
        Integrates all features:
        1. Evaluate new ideas
        2. Monitor active projects
        3. Optimize execution sequence
        4. Assign optimal locations
        5. Generate master recommendations
        
        Returns:
            Complete orchestration results with unified agent insights
        """
        print("🤖 Agent: Performing full portfolio orchestration")
        print("=" * 60)
        
        results = {
            'orchestrated_at': datetime.now().isoformat(),
            'new_ideas_evaluated': [],
            'active_projects_monitored': [],
            'sequencing_optimized': None,
            'locations_assigned': None,
            'master_recommendations': []
        }
        
        # 1. Evaluate new ideas
        print("\n📝 Step 1: Evaluating new ideas")
        for idea in new_ideas:
            evaluation = self.autonomous_idea_evaluation(idea)
            results['new_ideas_evaluated'].append(evaluation)
            
            if evaluation['agent_insights']['agent_recommendation']['action'] == 'FAST_TRACK':
                results['master_recommendations'].append({
                    'priority': 'HIGH',
                    'type': 'FAST_TRACK_APPROVAL',
                    'item': idea['project_id'],
                    'recommendation': 'Expedite approval and resource allocation'
                })
        
        # 2. Monitor active projects
        print("\n📊 Step 2: Monitoring active project benefits")
        for project in active_projects[:5]:  # Limit for demo
            monitoring = self.autonomous_benefit_monitoring(project['project_id'])
            results['active_projects_monitored'].append(monitoring)
            
            if monitoring['agent_synthesis']['health_status'] == 'CRITICAL':
                results['master_recommendations'].append({
                    'priority': 'CRITICAL',
                    'type': 'INTERVENTION_REQUIRED',
                    'item': project['project_id'],
                    'recommendation': 'Immediate executive attention needed'
                })
        
        # 3. Optimize sequencing
        if active_projects:
            print("\n📅 Step 3: Optimizing execution sequence")
            sequencing = self.autonomous_portfolio_sequencing(
                active_projects,
                max_parallel=5,
                resource_constraints=resource_constraints
            )
            results['sequencing_optimized'] = sequencing
        
        # 4. Assign locations
        if active_projects:
            print("\n🌍 Step 4: Optimizing location assignments")
            locations = self.autonomous_location_assignment(
                active_projects,
                location_resources=location_resources
            )
            results['locations_assigned'] = locations
        
        # 5. Master recommendations
        print("\n💡 Step 5: Generating master recommendations")
        results['master_recommendations'].append({
            'priority': 'MEDIUM',
            'type': 'PORTFOLIO_HEALTH',
            'recommendation': f'Portfolio contains {len(active_projects)} active projects with {len(new_ideas)} pending evaluations'
        })
        
        return results


# Convenience functions
def create_orchestrator(api_key: Optional[str] = None) -> IntegratedAgentOrchestrator:
    """Create an integrated orchestrator instance"""
    return IntegratedAgentOrchestrator(api_key=api_key, use_llm=api_key is not None)


if __name__ == "__main__":
    print("🤖 Integrated Agent Orchestrator")
    print("=" * 60)
    print("\nThis module provides agent-powered orchestration across:")
    print("  • Demand Evaluation")
    print("  • Benefit Intelligence")
    print("  • Sequencing Optimization")
    print("  • Location Resource Optimization")
    print("\nImport and use:")
    print("  from integrated_agent_orchestrator import create_orchestrator")
    print("  orchestrator = create_orchestrator(api_key='your-key')")
    print("  result = orchestrator.full_portfolio_orchestration(...)")
