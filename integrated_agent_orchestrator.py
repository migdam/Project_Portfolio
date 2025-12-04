#!/usr/bin/env python3
"""
Integrated Agent Orchestrator

Connects LangGraph deep agent to all portfolio intelligence features:
- Demand Evaluation
- Benefit Intelligence
- Sequencing Optimization
- Location Resource Optimization
- Risk & Cost Prediction
- Project Planning Suite (NEW)
- Team Recommendation Engine (NEW)

The agent acts as an intelligent coordinator that:
1. Analyzes incoming project ideas
2. Routes them through appropriate evaluation pipelines
3. Monitors benefit realization
4. Optimizes portfolio execution sequence
5. Assigns optimal locations
6. Generates comprehensive project plans
7. Recommends optimal team compositions
8. Provides autonomous recommendations

Author: Portfolio ML
Version: 2.0.0
"""

from typing import Dict, List, Optional
from langgraph_agent import PortfolioAgent
from demand_evaluation_toolkit import DemandEvaluationToolkit
from benefit_tracker import BenefitRealizationTracker
from benefit_trend_analyzer import BenefitTrendAnalyzer
from benefit_alert_system import BenefitAlertSystem
from sequencing_optimizer import SequencingOptimizer
from location_resource_optimizer import LocationResourceOptimizer
from project_plan_generator import ProjectPlanGenerator
from team_recommender import TeamRecommender
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
    - Project plan generation
    - Team composition recommendations
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
        self.plan_generator = ProjectPlanGenerator()
        self.team_recommender = TeamRecommender()
        
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
    
    def autonomous_plan_generation(
        self,
        project_idea: Dict,
        template: str = 'standard'
    ) -> Dict:
        """
        Agent-powered autonomous project plan generation
        
        Flow:
        1. Generate comprehensive project plan
        2. Analyze plan quality and completeness
        3. Identify optimization opportunities
        4. Provide intelligent recommendations
        
        Args:
            project_idea: Project information including:
                - project_id, project_name, description
                - business_problem, expected_benefits
                - duration_months, total_cost
                - dependencies, resource_requirements
            template: Plan template ('standard', 'agile', 'waterfall')
        
        Returns:
            Plan results with agent synthesis and recommendations
        """
        print(f"🤖 Agent: Generating project plan for '{project_idea.get('project_name', 'Untitled')}'")
        
        # Generate comprehensive plan
        plan = self.plan_generator.draft_project_plan(project_idea, template)
        
        # Agent analysis of the plan
        agent_synthesis = {
            'generated_at': datetime.now().isoformat(),
            'project_id': plan.charter.project_id,
            'plan_quality_score': 0,
            'completeness_score': 0,
            'agent_recommendations': [],
            'risk_assessment': None,
            'confidence': 0
        }
        
        # Assess plan quality
        quality_factors = []
        
        # Check completeness
        if len(plan.milestones) >= 5:
            quality_factors.append(('milestones', 100))
        else:
            quality_factors.append(('milestones', 70))
        
        if len(plan.work_breakdown) >= 4:
            quality_factors.append(('wbs', 100))
        else:
            quality_factors.append(('wbs', 80))
        
        if len(plan.risk_register) >= 5:
            quality_factors.append(('risks', 100))
        else:
            quality_factors.append(('risks', 75))
        
        if plan.budget['financial_summary']['roi_percent'] > 50:
            quality_factors.append(('financial', 100))
            agent_synthesis['agent_recommendations'].append({
                'type': 'FINANCIAL_OPPORTUNITY',
                'priority': 'HIGH',
                'recommendation': f"Strong ROI ({plan.budget['financial_summary']['roi_percent']:.1f}%) - prioritize for fast-track approval",
                'confidence': 0.90
            })
        else:
            quality_factors.append(('financial', 85))
        
        # Calculate quality score
        agent_synthesis['plan_quality_score'] = sum(score for _, score in quality_factors) / len(quality_factors)
        agent_synthesis['completeness_score'] = min(agent_synthesis['plan_quality_score'] + 5, 100)
        
        # Analyze timeline
        duration = plan.timeline.get('duration_months', 0)
        if duration > 24:
            agent_synthesis['agent_recommendations'].append({
                'type': 'TIMELINE_WARNING',
                'priority': 'MEDIUM',
                'recommendation': f'Long duration ({duration} months) - consider phased delivery or MVP approach',
                'confidence': 0.75
            })
        elif duration < 3:
            agent_synthesis['agent_recommendations'].append({
                'type': 'TIMELINE_RISK',
                'priority': 'HIGH',
                'recommendation': f'Very short timeline ({duration} months) - validate feasibility and resource availability',
                'confidence': 0.80
            })
        
        # Analyze resource plan
        team_size = plan.resource_plan.get('average_team_size', 0)
        if team_size > 15:
            agent_synthesis['agent_recommendations'].append({
                'type': 'RESOURCE_WARNING',
                'priority': 'MEDIUM',
                'recommendation': f'Large team ({team_size} FTE) - ensure strong coordination and communication processes',
                'confidence': 0.70
            })
        elif team_size < 2:
            agent_synthesis['agent_recommendations'].append({
                'type': 'RESOURCE_RISK',
                'priority': 'HIGH',
                'recommendation': f'Very small team ({team_size} FTE) - validate scope and consider resource augmentation',
                'confidence': 0.85
            })
        
        # Analyze risks
        high_risks = [r for r in plan.risk_register if r['risk_score'] >= 60]
        if high_risks:
            agent_synthesis['risk_assessment'] = {
                'high_risk_count': len(high_risks),
                'top_risk': high_risks[0]['description'],
                'mitigation_priority': 'CRITICAL' if len(high_risks) >= 3 else 'HIGH'
            }
            agent_synthesis['agent_recommendations'].append({
                'type': 'RISK_MITIGATION',
                'priority': 'HIGH',
                'recommendation': f'{len(high_risks)} high-severity risks identified - develop mitigation plans before approval',
                'confidence': 0.85
            })
        else:
            agent_synthesis['risk_assessment'] = {
                'high_risk_count': 0,
                'status': 'LOW_RISK',
                'mitigation_priority': 'STANDARD'
            }
        
        # Analyze governance gates
        gate_count = sum(1 for m in plan.milestones if m.governance_gate)
        if gate_count < 3:
            agent_synthesis['agent_recommendations'].append({
                'type': 'GOVERNANCE_GUIDANCE',
                'priority': 'LOW',
                'recommendation': f'Consider adding more governance gates (current: {gate_count}) for better control',
                'confidence': 0.60
            })
        
        # Calculate overall confidence
        confidence_base = 85.0
        if agent_synthesis['plan_quality_score'] >= 90:
            confidence_base += 10
        elif agent_synthesis['plan_quality_score'] < 75:
            confidence_base -= 15
        
        if len(high_risks) >= 3:
            confidence_base -= 10
        
        agent_synthesis['confidence'] = max(min(confidence_base, 95.0), 50.0)
        
        # Strategic alignment insight
        alignment_score = plan.charter.strategic_alignment.get('alignment_score', 0)
        if alignment_score >= 80:
            agent_synthesis['agent_recommendations'].append({
                'type': 'STRATEGIC_ALIGNMENT',
                'priority': 'HIGH',
                'recommendation': f'Strong strategic alignment ({alignment_score:.1f}/100) - aligns well with organizational goals',
                'confidence': 0.90
            })
        elif alignment_score < 60:
            agent_synthesis['agent_recommendations'].append({
                'type': 'STRATEGIC_CONCERN',
                'priority': 'MEDIUM',
                'recommendation': f'Limited strategic alignment ({alignment_score:.1f}/100) - validate strategic fit before proceeding',
                'confidence': 0.75
            })
        
        return {
            'plan': plan,
            'agent_synthesis': agent_synthesis,
            'summary': {
                'project_name': plan.charter.project_name,
                'duration_months': duration,
                'total_cost': plan.budget['total_cost'],
                'roi_percent': plan.budget['financial_summary']['roi_percent'],
                'team_size_fte': team_size,
                'milestone_count': len(plan.milestones),
                'high_risk_count': len(high_risks)
            }
        }
    
    def autonomous_team_recommendation(
        self,
        project_requirements: Dict,
        available_resources: List,
        optimization_objective: str = 'balanced'
    ) -> Dict:
        """
        Agent-powered autonomous team recommendation
        
        Flow:
        1. Generate team recommendations
        2. Analyze team quality and risks
        3. Compare alternatives
        4. Provide intelligent selection guidance
        
        Args:
            project_requirements: Dict with:
                - required_skills: List[Dict]
                - duration_months: int
                - project_complexity: str
                - project_type: str
                - budget_constraint: float (optional)
            available_resources: List of Person objects
            optimization_objective: 'cost', 'quality', 'balanced'
        
        Returns:
            Team recommendations with agent synthesis
        """
        print(f"🤖 Agent: Recommending team for {project_requirements.get('project_type', 'project')}")
        
        # Generate team recommendations
        recommendations = self.team_recommender.recommend_team(
            project_requirements,
            available_resources,
            optimization_objective
        )
        
        # Agent analysis
        agent_synthesis = {
            'analyzed_at': datetime.now().isoformat(),
            'optimization_objective': optimization_objective,
            'recommendation_count': len(recommendations),
            'agent_guidance': [],
            'team_quality_assessment': None,
            'confidence': 0
        }
        
        if not recommendations:
            agent_synthesis['agent_guidance'].append({
                'type': 'NO_VIABLE_TEAM',
                'priority': 'CRITICAL',
                'recommendation': 'Unable to form viable team - consider relaxing constraints or acquiring external resources',
                'confidence': 0.95
            })
            agent_synthesis['confidence'] = 30.0
            return {
                'recommendations': [],
                'agent_synthesis': agent_synthesis
            }
        
        # Analyze primary recommendation
        primary = recommendations[0]
        
        # Quality assessment
        agent_synthesis['team_quality_assessment'] = {
            'skill_match': primary.overall_skill_match,
            'predicted_performance': primary.predicted_performance,
            'team_size_fte': primary.team_size_fte,
            'cost_efficiency': 100 - (primary.total_cost / max(project_requirements.get('budget_constraint', primary.total_cost * 1.5), 1) * 100)
        }
        
        # Analyze skill match
        if primary.overall_skill_match >= 90:
            agent_synthesis['agent_guidance'].append({
                'type': 'EXCELLENT_MATCH',
                'priority': 'HIGH',
                'recommendation': f'Excellent skill match ({primary.overall_skill_match:.1f}%) - team well-suited for project requirements',
                'confidence': 0.95
            })
        elif primary.overall_skill_match < 70:
            agent_synthesis['agent_guidance'].append({
                'type': 'SKILL_CONCERN',
                'priority': 'HIGH',
                'recommendation': f'Limited skill match ({primary.overall_skill_match:.1f}%) - consider training or external resources',
                'confidence': 0.80
            })
        
        # Analyze skill gaps
        if primary.skill_gaps:
            agent_synthesis['agent_guidance'].append({
                'type': 'SKILL_GAPS',
                'priority': 'HIGH',
                'recommendation': f'{len(primary.skill_gaps)} skill gaps identified - plan for training, contractors, or hiring',
                'confidence': 0.85,
                'gaps': primary.skill_gaps
            })
        
        # Analyze risk factors
        if len(primary.risk_factors) >= 3:
            agent_synthesis['agent_guidance'].append({
                'type': 'TEAM_RISKS',
                'priority': 'HIGH',
                'recommendation': f'{len(primary.risk_factors)} team risks identified - develop mitigation strategies',
                'confidence': 0.80,
                'risks': primary.risk_factors
            })
        
        # Analyze cost
        budget = project_requirements.get('budget_constraint')
        if budget and primary.total_cost > budget:
            agent_synthesis['agent_guidance'].append({
                'type': 'BUDGET_OVERRUN',
                'priority': 'CRITICAL',
                'recommendation': f'Team cost ${primary.total_cost:,.0f} exceeds budget ${budget:,.0f} - consider alternatives',
                'confidence': 0.95
            })
        elif budget and primary.total_cost < budget * 0.7:
            agent_synthesis['agent_guidance'].append({
                'type': 'COST_EFFICIENT',
                'priority': 'MEDIUM',
                'recommendation': f'Team cost well under budget - opportunity to enhance capabilities',
                'confidence': 0.75
            })
        
        # Compare alternatives
        if len(recommendations) > 1:
            cost_comparison = []
            quality_comparison = []
            
            for i, rec in enumerate(recommendations):
                label = 'Primary' if i == 0 else f'Alt {i}'
                cost_comparison.append((label, rec.total_cost))
                quality_comparison.append((label, rec.predicted_performance))
            
            # Sort alternatives
            cost_comparison.sort(key=lambda x: x[1])
            quality_comparison.sort(key=lambda x: x[1], reverse=True)
            
            cheapest = cost_comparison[0]
            best_quality = quality_comparison[0]
            
            agent_synthesis['alternatives_analysis'] = {
                'cheapest_option': cheapest[0],
                'cheapest_cost': cheapest[1],
                'highest_quality_option': best_quality[0],
                'highest_quality_score': best_quality[1]
            }
            
            if cheapest[0] != 'Primary':
                agent_synthesis['agent_guidance'].append({
                    'type': 'COST_ALTERNATIVE',
                    'priority': 'MEDIUM',
                    'recommendation': f'{cheapest[0]} offers lower cost (${cheapest[1]:,.0f}) - review tradeoffs',
                    'confidence': 0.70
                })
            
            if best_quality[0] != 'Primary':
                agent_synthesis['agent_guidance'].append({
                    'type': 'QUALITY_ALTERNATIVE',
                    'priority': 'MEDIUM',
                    'recommendation': f'{best_quality[0]} offers higher predicted performance ({best_quality[1]:.1f}) - review tradeoffs',
                    'confidence': 0.70
                })
        
        # Calculate confidence
        confidence_base = primary.confidence
        
        if primary.overall_skill_match >= 85 and not primary.skill_gaps:
            confidence_base += 10
        elif primary.skill_gaps and len(primary.skill_gaps) >= 3:
            confidence_base -= 15
        
        if len(primary.risk_factors) >= 4:
            confidence_base -= 10
        
        agent_synthesis['confidence'] = max(min(confidence_base, 95.0), 40.0)
        
        return {
            'recommendations': recommendations,
            'agent_synthesis': agent_synthesis,
            'primary_summary': {
                'team_size_fte': primary.team_size_fte,
                'total_cost': primary.total_cost,
                'skill_match': primary.overall_skill_match,
                'predicted_performance': primary.predicted_performance,
                'risk_count': len(primary.risk_factors),
                'skill_gap_count': len(primary.skill_gaps)
            }
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
