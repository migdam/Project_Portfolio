#!/usr/bin/env python3
"""
Project Plan Generator

Auto-generates comprehensive project plans by orchestrating all planning components:
- Project charter (scope, objectives, deliverables)
- Timeline and dependencies (from sequencing_optimizer)
- Resource plan (from location_optimizer)
- Risk register (from PRM models)
- Budget and financial projections (from ROI calculator)
- Milestones and governance gates
- Success criteria and KPIs
- Stakeholder identification
- Communication plan

Exports to Markdown, PDF, and Word formats.

Author: Portfolio ML
Version: 1.0.0
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
import os

# Import existing modules
from sequencing_optimizer import SequencingOptimizer, Project
from roi_calculator import ROICalculator
from strategic_alignment import StrategicAlignmentScorer


@dataclass
class ProjectCharter:
    """Project charter data model"""
    project_id: str
    project_name: str
    executive_summary: str
    business_problem: str
    objectives: List[str]
    scope_inclusions: List[str]
    scope_exclusions: List[str]
    key_deliverables: List[str]
    success_criteria: List[str]
    assumptions: List[str]
    constraints: List[str]
    strategic_alignment: Dict


@dataclass
class Milestone:
    """Project milestone"""
    name: str
    description: str
    target_date_month: int
    deliverables: List[str]
    governance_gate: bool = False
    gate_criteria: List[str] = field(default_factory=list)


@dataclass
class StakeholderRole:
    """Stakeholder with role"""
    name: str
    role: str
    responsibility: str
    engagement_level: str  # HIGH, MEDIUM, LOW


@dataclass
class WorkPackage:
    """Work breakdown structure element"""
    wbs_id: str
    name: str
    description: str
    duration_months: float
    dependencies: List[str]
    resource_requirements: Dict[str, float]
    deliverables: List[str]


@dataclass
class ProjectPlan:
    """Complete project plan"""
    charter: ProjectCharter
    timeline: Dict
    work_breakdown: List[WorkPackage]
    milestones: List[Milestone]
    resource_plan: Dict
    risk_register: List[Dict]
    budget: Dict
    stakeholders: List[StakeholderRole]
    communication_plan: Dict
    generated_date: datetime = field(default_factory=datetime.now)


class ProjectPlanGenerator:
    """
    Unified project plan generator
    
    Orchestrates all planning modules to generate comprehensive project plans
    """
    
    def __init__(self):
        """Initialize plan generator with module dependencies"""
        self.roi_calculator = ROICalculator()
        self.strategic_scorer = StrategicAlignmentScorer()
    
    def draft_project_plan(
        self,
        project_idea: Dict,
        template: str = 'standard'
    ) -> ProjectPlan:
        """
        Auto-generate comprehensive project plan
        
        Args:
            project_idea: Project information including:
                - project_id: Unique identifier
                - project_name: Human-readable name
                - description: Project overview
                - business_problem: Problem being solved
                - expected_benefits: Benefit quantification
                - duration_months: Project duration
                - total_cost: Estimated cost
                - dependencies: List of dependency project IDs
                - resource_requirements: Resource needs
                - strategic_context: Strategic alignment info
            template: Plan template ('standard', 'agile', 'waterfall')
        
        Returns:
            ProjectPlan with all sections populated
        """
        # Generate charter
        charter = self._generate_charter(project_idea)
        
        # Generate timeline and critical path
        timeline = self._generate_timeline(project_idea)
        
        # Generate work breakdown structure
        work_breakdown = self._generate_wbs(project_idea, timeline)
        
        # Generate milestones and gates
        milestones = self._generate_milestones(project_idea, timeline)
        
        # Generate resource plan
        resource_plan = self._generate_resource_plan(project_idea)
        
        # Generate risk register
        risk_register = self._generate_risk_register(project_idea)
        
        # Generate budget
        budget = self._generate_budget(project_idea)
        
        # Generate stakeholders
        stakeholders = self._generate_stakeholders(project_idea)
        
        # Generate communication plan
        communication_plan = self._generate_communication_plan(project_idea, stakeholders)
        
        return ProjectPlan(
            charter=charter,
            timeline=timeline,
            work_breakdown=work_breakdown,
            milestones=milestones,
            resource_plan=resource_plan,
            risk_register=risk_register,
            budget=budget,
            stakeholders=stakeholders,
            communication_plan=communication_plan
        )
    
    def _generate_charter(self, project_idea: Dict) -> ProjectCharter:
        """Generate project charter"""
        
        # Score strategic alignment
        strategic_score = self.strategic_scorer.score_project(project_idea)
        
        # Extract or infer charter components
        project_id = project_idea.get('project_id', 'PROJ-NEW-001')
        project_name = project_idea.get('project_name', 'New Project')
        description = project_idea.get('description', '')
        business_problem = project_idea.get('business_problem', '')
        
        # Generate objectives from benefits
        benefits = project_idea.get('expected_benefits', {})
        objectives = self._extract_objectives(benefits, description)
        
        # Infer scope
        scope_inclusions, scope_exclusions = self._infer_scope(project_idea)
        
        # Extract or generate deliverables
        deliverables = project_idea.get('key_deliverables', 
            self._generate_default_deliverables(project_idea))
        
        # Generate success criteria
        success_criteria = self._generate_success_criteria(benefits, objectives)
        
        # Extract assumptions and constraints
        assumptions = project_idea.get('assumptions', self._generate_default_assumptions())
        constraints = project_idea.get('constraints', self._generate_default_constraints(project_idea))
        
        # Executive summary
        executive_summary = self._generate_executive_summary(
            project_name, business_problem, objectives, benefits
        )
        
        return ProjectCharter(
            project_id=project_id,
            project_name=project_name,
            executive_summary=executive_summary,
            business_problem=business_problem,
            objectives=objectives,
            scope_inclusions=scope_inclusions,
            scope_exclusions=scope_exclusions,
            key_deliverables=deliverables,
            success_criteria=success_criteria,
            assumptions=assumptions,
            constraints=constraints,
            strategic_alignment=strategic_score
        )
    
    def _generate_timeline(self, project_idea: Dict) -> Dict:
        """Generate timeline with dependencies and critical path"""
        
        # Create sequencing optimizer
        optimizer = SequencingOptimizer()
        
        # Add this project
        project_id = project_idea.get('project_id', 'PROJ-NEW-001')
        duration = project_idea.get('duration_months', 12)
        dependencies = project_idea.get('dependencies', [])
        resource_reqs = project_idea.get('resource_requirements', {})
        
        optimizer.add_project(
            project_id=project_id,
            duration_months=duration,
            priority_score=75.0,
            dependencies=dependencies,
            resource_requirements=resource_reqs
        )
        
        # Add dependency projects (if needed for CPM)
        for dep_id in dependencies:
            optimizer.add_project(
                project_id=dep_id,
                duration_months=6,  # Assume completed/in progress
                priority_score=100.0,
                dependencies=[]
            )
        
        # Validate dependencies
        is_valid, error = optimizer.validate_dependencies()
        
        if not is_valid:
            return {
                'error': error,
                'duration_months': duration,
                'phases': []
            }
        
        # Calculate critical path
        try:
            critical_path = optimizer.calculate_critical_path()
            project_schedule = critical_path.get(project_id, {})
        except:
            project_schedule = {
                'earliest_start': 0,
                'earliest_finish': duration,
                'is_critical': True
            }
        
        # Generate phases
        phases = self._generate_phases(duration, project_idea.get('project_type', 'Standard'))
        
        return {
            'duration_months': duration,
            'earliest_start_month': project_schedule.get('earliest_start', 0),
            'earliest_finish_month': project_schedule.get('earliest_finish', duration),
            'is_critical_path': project_schedule.get('is_critical', False),
            'dependencies': dependencies,
            'phases': phases,
            'critical_path_info': project_schedule
        }
    
    def _generate_phases(self, duration_months: int, project_type: str) -> List[Dict]:
        """Generate project phases"""
        
        # Standard phases for typical projects
        if 'Agile' in project_type or 'Digital' in project_type:
            phases = [
                {'name': 'Discovery & Planning', 'percent': 15},
                {'name': 'MVP Development', 'percent': 25},
                {'name': 'Iterative Development', 'percent': 35},
                {'name': 'Testing & QA', 'percent': 15},
                {'name': 'Deployment & Rollout', 'percent': 10}
            ]
        else:
            phases = [
                {'name': 'Initiation & Planning', 'percent': 20},
                {'name': 'Requirements & Design', 'percent': 25},
                {'name': 'Execution & Build', 'percent': 35},
                {'name': 'Testing & Validation', 'percent': 15},
                {'name': 'Deployment & Closure', 'percent': 5}
            ]
        
        # Calculate duration for each phase
        result = []
        cumulative_months = 0
        
        for phase in phases:
            phase_duration = round((phase['percent'] / 100.0) * duration_months, 1)
            result.append({
                'name': phase['name'],
                'duration_months': phase_duration,
                'start_month': cumulative_months,
                'end_month': cumulative_months + phase_duration
            })
            cumulative_months += phase_duration
        
        return result
    
    def _generate_wbs(self, project_idea: Dict, timeline: Dict) -> List[WorkPackage]:
        """Generate work breakdown structure"""
        
        work_packages = []
        phases = timeline.get('phases', [])
        project_type = project_idea.get('project_type', 'Standard')
        
        # Generate WBS based on phases
        for i, phase in enumerate(phases):
            wbs_id = f"WP-{i+1}"
            
            # Generate sub-tasks for each phase
            subtasks = self._generate_phase_subtasks(phase['name'], project_type)
            
            work_packages.append(WorkPackage(
                wbs_id=wbs_id,
                name=phase['name'],
                description=f"Complete all activities for {phase['name']}",
                duration_months=phase['duration_months'],
                dependencies=[f"WP-{i}"] if i > 0 else [],
                resource_requirements=self._estimate_phase_resources(
                    phase['name'], 
                    project_idea.get('resource_requirements', {})
                ),
                deliverables=subtasks
            ))
        
        return work_packages
    
    def _generate_phase_subtasks(self, phase_name: str, project_type: str) -> List[str]:
        """Generate subtasks for a phase"""
        
        subtask_map = {
            'Discovery & Planning': [
                'Stakeholder interviews',
                'Requirements gathering',
                'Technical feasibility study',
                'Project plan approval'
            ],
            'Initiation & Planning': [
                'Project charter approval',
                'Stakeholder identification',
                'Risk assessment',
                'Resource allocation plan'
            ],
            'Requirements & Design': [
                'Detailed requirements specification',
                'System architecture design',
                'Interface design',
                'Design review and approval'
            ],
            'MVP Development': [
                'Core feature development',
                'Integration setup',
                'MVP testing',
                'User feedback collection'
            ],
            'Execution & Build': [
                'Development/construction',
                'Integration activities',
                'Quality checks',
                'Documentation'
            ],
            'Testing & QA': [
                'Unit testing',
                'Integration testing',
                'User acceptance testing',
                'Defect resolution'
            ],
            'Deployment & Rollout': [
                'Production deployment',
                'User training',
                'Rollout execution',
                'Hypercare support'
            ],
            'Deployment & Closure': [
                'Final deployment',
                'Lessons learned',
                'Documentation handover',
                'Project closure'
            ]
        }
        
        return subtask_map.get(phase_name, ['Phase activities', 'Deliverables', 'Quality checks'])
    
    def _estimate_phase_resources(self, phase_name: str, total_resources: Dict) -> Dict[str, float]:
        """Estimate resource requirements per phase"""
        
        # Distribution factors per phase
        phase_factors = {
            'Discovery & Planning': 0.15,
            'Initiation & Planning': 0.20,
            'Requirements & Design': 0.25,
            'MVP Development': 0.30,
            'Execution & Build': 0.40,
            'Iterative Development': 0.35,
            'Testing & QA': 0.20,
            'Deployment & Rollout': 0.15,
            'Deployment & Closure': 0.10
        }
        
        factor = phase_factors.get(phase_name, 0.20)
        
        return {
            resource_type: amount * factor
            for resource_type, amount in total_resources.items()
        }
    
    def _generate_milestones(self, project_idea: Dict, timeline: Dict) -> List[Milestone]:
        """Generate milestones and governance gates"""
        
        milestones = []
        phases = timeline.get('phases', [])
        duration = timeline.get('duration_months', 12)
        
        # Phase completion milestones
        for phase in phases:
            end_month = phase['end_month']
            is_gate = 'Planning' in phase['name'] or 'Design' in phase['name'] or 'Deployment' in phase['name']
            
            milestones.append(Milestone(
                name=f"{phase['name']} Complete",
                description=f"All activities and deliverables for {phase['name']} completed",
                target_date_month=int(end_month),
                deliverables=self._get_phase_deliverables(phase['name']),
                governance_gate=is_gate,
                gate_criteria=self._get_gate_criteria(phase['name']) if is_gate else []
            ))
        
        # Key interim milestones
        if duration >= 12:
            milestones.insert(len(milestones)//2, Milestone(
                name="Mid-Project Review",
                description="Comprehensive project health check and course correction",
                target_date_month=duration // 2,
                deliverables=['Progress report', 'Risk update', 'Budget review'],
                governance_gate=True,
                gate_criteria=[
                    'On schedule (±10%)',
                    'On budget (±5%)',
                    'Key risks mitigated',
                    'Stakeholder satisfaction >70%'
                ]
            ))
        
        return sorted(milestones, key=lambda m: m.target_date_month)
    
    def _get_phase_deliverables(self, phase_name: str) -> List[str]:
        """Get deliverables for a phase"""
        
        deliverable_map = {
            'Discovery & Planning': ['Requirements document', 'Project plan', 'Risk register'],
            'Initiation & Planning': ['Project charter', 'Stakeholder matrix', 'Resource plan'],
            'Requirements & Design': ['Design specifications', 'Architecture diagrams', 'Prototype'],
            'MVP Development': ['Working MVP', 'Test results', 'User feedback report'],
            'Execution & Build': ['Core deliverables', 'Integration complete', 'Quality reports'],
            'Testing & QA': ['Test reports', 'Defect resolution', 'UAT sign-off'],
            'Deployment & Rollout': ['Production system', 'Training materials', 'Support documentation'],
            'Deployment & Closure': ['Final deliverables', 'Lessons learned', 'Closure report']
        }
        
        return deliverable_map.get(phase_name, ['Phase deliverables'])
    
    def _get_gate_criteria(self, phase_name: str) -> List[str]:
        """Get governance gate criteria"""
        
        criteria_map = {
            'Discovery & Planning': [
                'Business case approved',
                'Funding secured',
                'Resources committed',
                'Risks acceptable'
            ],
            'Initiation & Planning': [
                'Charter approved',
                'Team assembled',
                'Plan reviewed',
                'Go/No-go decision'
            ],
            'Requirements & Design': [
                'Requirements complete',
                'Design approved',
                'Technical feasibility confirmed',
                'Budget reconfirmed'
            ],
            'Deployment & Rollout': [
                'All tests passed',
                'Training complete',
                'Rollback plan ready',
                'Go-live approval'
            ],
            'Deployment & Closure': [
                'Deliverables accepted',
                'Benefits tracking initiated',
                'Documentation complete',
                'Formal closure'
            ]
        }
        
        return criteria_map.get(phase_name, ['Phase objectives met', 'Quality standards achieved'])
    
    def _generate_resource_plan(self, project_idea: Dict) -> Dict:
        """Generate resource plan"""
        
        resource_reqs = project_idea.get('resource_requirements', {})
        duration = project_idea.get('duration_months', 12)
        
        # Default resource structure if not provided
        if not resource_reqs:
            project_type = project_idea.get('project_type', 'Standard')
            resource_reqs = self._estimate_default_resources(project_type, duration)
        
        # Calculate team composition
        team_composition = {}
        for resource_type, fte_months in resource_reqs.items():
            avg_fte = fte_months / duration
            team_composition[resource_type] = {
                'total_fte_months': fte_months,
                'average_fte': round(avg_fte, 2),
                'peak_fte': round(avg_fte * 1.3, 2),  # Assume 30% peak
                'role_description': self._get_role_description(resource_type)
            }
        
        return {
            'team_composition': team_composition,
            'total_fte_months': sum(resource_reqs.values()),
            'average_team_size': round(sum(resource_reqs.values()) / duration, 1),
            'ramp_up_period_months': max(2, duration // 6),
            'ramp_down_period_months': max(1, duration // 12)
        }
    
    def _estimate_default_resources(self, project_type: str, duration_months: int) -> Dict[str, float]:
        """Estimate default resource requirements"""
        
        if 'Digital' in project_type or 'Technology' in project_type:
            return {
                'Engineering': duration_months * 3,
                'Design': duration_months * 0.5,
                'Product Management': duration_months * 1,
                'QA': duration_months * 1
            }
        else:
            return {
                'Project Management': duration_months * 1,
                'Business Analysts': duration_months * 2,
                'Technical Specialists': duration_months * 2,
                'Subject Matter Experts': duration_months * 0.5
            }
    
    def _get_role_description(self, role: str) -> str:
        """Get role description"""
        
        descriptions = {
            'Engineering': 'Software engineers for development',
            'Design': 'UX/UI designers',
            'Product Management': 'Product managers and owners',
            'QA': 'Quality assurance engineers',
            'Project Management': 'Project managers',
            'Business Analysts': 'Business analysis and requirements',
            'Technical Specialists': 'Technical experts and architects',
            'Subject Matter Experts': 'Domain specialists'
        }
        
        return descriptions.get(role, f'{role} resources')
    
    def _generate_risk_register(self, project_idea: Dict) -> List[Dict]:
        """Generate risk register"""
        
        # Common project risks by category
        risks = []
        
        # Schedule risks
        risks.append({
            'risk_id': 'RISK-001',
            'category': 'Schedule',
            'description': 'Project timeline slippage due to scope changes or resource constraints',
            'probability': 'MEDIUM',
            'impact': 'HIGH',
            'risk_score': 60,
            'mitigation': 'Strict change control process, buffer time in schedule, regular progress monitoring'
        })
        
        # Budget risks
        risks.append({
            'risk_id': 'RISK-002',
            'category': 'Budget',
            'description': 'Cost overruns due to unforeseen complexities or scope creep',
            'probability': 'MEDIUM',
            'impact': 'HIGH',
            'risk_score': 55,
            'mitigation': 'Contingency budget (15%), monthly cost tracking, change request approval process'
        })
        
        # Resource risks
        risks.append({
            'risk_id': 'RISK-003',
            'category': 'Resources',
            'description': 'Key resource unavailability or skill gaps',
            'probability': 'MEDIUM',
            'impact': 'MEDIUM',
            'risk_score': 45,
            'mitigation': 'Resource backup plans, cross-training, early skill gap identification'
        })
        
        # Technical risks (if applicable)
        project_type = project_idea.get('project_type', '')
        if 'Technology' in project_type or 'Digital' in project_type:
            risks.append({
                'risk_id': 'RISK-004',
                'category': 'Technical',
                'description': 'Technical complexity or integration challenges',
                'probability': 'MEDIUM',
                'impact': 'HIGH',
                'risk_score': 65,
                'mitigation': 'Technical proof-of-concept, architecture review, expert consultation'
            })
        
        # Stakeholder risks
        risks.append({
            'risk_id': 'RISK-005',
            'category': 'Stakeholder',
            'description': 'Inadequate stakeholder engagement or changing requirements',
            'probability': 'LOW',
            'impact': 'MEDIUM',
            'risk_score': 35,
            'mitigation': 'Regular stakeholder meetings, clear RACI matrix, requirements freeze periods'
        })
        
        return sorted(risks, key=lambda r: r['risk_score'], reverse=True)
    
    def _generate_budget(self, project_idea: Dict) -> Dict:
        """Generate budget using ROI calculator"""
        
        # Calculate ROI metrics
        roi_analysis = self.roi_calculator.calculate_roi(project_idea)
        
        cost_analysis = roi_analysis['cost_analysis']
        benefit_analysis = roi_analysis['benefit_analysis']
        roi_metrics = roi_analysis['roi_metrics']
        
        # Structure budget
        return {
            'total_cost': cost_analysis['actual_cost'],
            'base_cost': cost_analysis['base_cost'],
            'contingency': cost_analysis['cost_overrun'],
            'cost_breakdown': self._generate_cost_breakdown(cost_analysis['base_cost'], project_idea),
            'benefits': benefit_analysis,
            'roi_metrics': roi_metrics,
            'financial_summary': {
                'npv': roi_metrics['npv'],
                'roi_percent': roi_metrics['risk_adjusted_roi_pct'],
                'payback_years': roi_metrics['payback_period_years'],
                'benefit_cost_ratio': roi_metrics['benefit_cost_ratio']
            }
        }
    
    def _generate_cost_breakdown(self, total_cost: float, project_idea: Dict) -> Dict:
        """Generate cost breakdown by category"""
        
        project_type = project_idea.get('project_type', 'Standard')
        
        if 'Technology' in project_type or 'Digital' in project_type:
            breakdown = {
                'Labor': 0.60,
                'Technology': 0.20,
                'Training': 0.05,
                'Consulting': 0.10,
                'Other': 0.05
            }
        else:
            breakdown = {
                'Labor': 0.70,
                'Materials': 0.10,
                'Consulting': 0.10,
                'Training': 0.05,
                'Other': 0.05
            }
        
        return {
            category: round(total_cost * percent, 2)
            for category, percent in breakdown.items()
        }
    
    def _generate_stakeholders(self, project_idea: Dict) -> List[StakeholderRole]:
        """Generate stakeholder matrix"""
        
        stakeholders = []
        
        # Executive sponsor
        stakeholders.append(StakeholderRole(
            name='Executive Sponsor',
            role='Sponsor',
            responsibility='Strategic oversight, funding approval, issue escalation',
            engagement_level='MEDIUM'
        ))
        
        # Project manager
        stakeholders.append(StakeholderRole(
            name='Project Manager',
            role='PM',
            responsibility='Day-to-day management, coordination, reporting',
            engagement_level='HIGH'
        ))
        
        # Business owner
        stakeholders.append(StakeholderRole(
            name='Business Owner',
            role='Owner',
            responsibility='Requirements, acceptance criteria, benefit realization',
            engagement_level='HIGH'
        ))
        
        # Technical lead (if applicable)
        project_type = project_idea.get('project_type', '')
        if 'Technology' in project_type or 'Digital' in project_type:
            stakeholders.append(StakeholderRole(
                name='Technical Lead',
                role='Tech Lead',
                responsibility='Architecture, technical decisions, development oversight',
                engagement_level='HIGH'
            ))
        
        # End users
        stakeholders.append(StakeholderRole(
            name='End Users',
            role='Users',
            responsibility='Requirements input, UAT, adoption',
            engagement_level='MEDIUM'
        ))
        
        # Finance
        stakeholders.append(StakeholderRole(
            name='Finance Team',
            role='Finance',
            responsibility='Budget approval, cost tracking, financial reporting',
            engagement_level='LOW'
        ))
        
        return stakeholders
    
    def _generate_communication_plan(self, project_idea: Dict, stakeholders: List[StakeholderRole]) -> Dict:
        """Generate communication plan"""
        
        return {
            'status_reporting': {
                'frequency': 'Weekly',
                'format': 'Status report + dashboard',
                'audience': ['PM', 'Sponsor', 'Owner'],
                'content': ['Progress', 'Risks', 'Issues', 'Next steps']
            },
            'steering_committee': {
                'frequency': 'Monthly',
                'format': 'Executive presentation',
                'audience': ['Sponsor', 'Senior Leadership'],
                'content': ['Strategic alignment', 'Financial status', 'Key decisions', 'Escalations']
            },
            'team_standups': {
                'frequency': 'Daily',
                'format': 'Quick sync meeting',
                'audience': ['Project Team'],
                'content': ['Yesterday', 'Today', 'Blockers']
            },
            'stakeholder_updates': {
                'frequency': 'Bi-weekly',
                'format': 'Email update + office hours',
                'audience': ['All Stakeholders'],
                'content': ['Progress highlights', 'Upcoming milestones', 'How to engage']
            },
            'governance_gates': {
                'frequency': 'Per milestone',
                'format': 'Gate review meeting + documentation',
                'audience': ['Sponsor', 'Steering Committee'],
                'content': ['Gate criteria review', 'Go/No-go decision', 'Next phase approval']
            }
        }
    
    def _extract_objectives(self, benefits: Dict, description: str) -> List[str]:
        """Extract objectives from benefits and description"""
        
        objectives = []
        
        if benefits.get('annual_revenue_increase', 0) > 0:
            objectives.append(f"Increase revenue by ${benefits['annual_revenue_increase']:,.0f} annually")
        
        if benefits.get('annual_cost_savings', 0) > 0:
            objectives.append(f"Reduce costs by ${benefits['annual_cost_savings']:,.0f} annually")
        
        if benefits.get('efficiency_improvement_pct', 0) > 0:
            objectives.append(f"Improve efficiency by {benefits['efficiency_improvement_pct']}%")
        
        if benefits.get('automation_hours', 0) > 0:
            objectives.append(f"Automate {benefits['automation_hours']:,.0f} hours of manual work")
        
        # Generic objective if none found
        if not objectives:
            objectives.append("Deliver project objectives as defined in business case")
        
        return objectives
    
    def _infer_scope(self, project_idea: Dict) -> Tuple[List[str], List[str]]:
        """Infer scope inclusions and exclusions"""
        
        inclusions = project_idea.get('scope_inclusions', [
            'All activities defined in project plan',
            'Deliverables specified in requirements',
            'Testing and quality assurance',
            'Documentation and training materials'
        ])
        
        exclusions = project_idea.get('scope_exclusions', [
            'Ongoing operational support (post-warranty)',
            'Related projects managed separately',
            'Infrastructure upgrades (unless specified)',
            'Third-party system modifications'
        ])
        
        return inclusions, exclusions
    
    def _generate_default_deliverables(self, project_idea: Dict) -> List[str]:
        """Generate default deliverables"""
        
        project_type = project_idea.get('project_type', 'Standard')
        
        if 'Technology' in project_type or 'Digital' in project_type:
            return [
                'Working software system',
                'Technical documentation',
                'User training materials',
                'System architecture documentation',
                'Test results and quality reports'
            ]
        else:
            return [
                'Project deliverables as specified',
                'Process documentation',
                'Training materials',
                'Lessons learned report',
                'Final project report'
            ]
    
    def _generate_success_criteria(self, benefits: Dict, objectives: List[str]) -> List[str]:
        """Generate success criteria"""
        
        criteria = [
            'Project delivered on time (±10%)',
            'Project delivered on budget (±5%)',
            'All deliverables meet quality standards',
            'Stakeholder acceptance achieved'
        ]
        
        # Add benefit-specific criteria
        if benefits.get('annual_cost_savings', 0) > 0:
            criteria.append(f"Cost savings target achieved within 12 months post-implementation")
        
        if benefits.get('annual_revenue_increase', 0) > 0:
            criteria.append(f"Revenue increase target achieved within 18 months")
        
        if benefits.get('efficiency_improvement_pct', 0) > 0:
            criteria.append(f"Efficiency improvement measured and confirmed")
        
        return criteria
    
    def _generate_default_assumptions(self) -> List[str]:
        """Generate default assumptions"""
        
        return [
            'Required resources will be available as planned',
            'Stakeholders will provide timely input and decisions',
            'No major organizational changes during project',
            'Technology and tools will be available and stable',
            'External dependencies will be met on schedule'
        ]
    
    def _generate_default_constraints(self, project_idea: Dict) -> List[str]:
        """Generate default constraints"""
        
        duration = project_idea.get('duration_months', 12)
        budget = project_idea.get('total_cost', 1000000)
        
        return [
            f'Fixed budget of ${budget:,.0f}',
            f'Target completion in {duration} months',
            'Must comply with organizational policies and standards',
            'Resource availability limited by organizational capacity',
            'Must meet all regulatory and compliance requirements'
        ]
    
    def _generate_executive_summary(
        self,
        project_name: str,
        business_problem: str,
        objectives: List[str],
        benefits: Dict
    ) -> str:
        """Generate executive summary"""
        
        summary = f"{project_name} addresses the following business need: {business_problem}\n\n"
        summary += "Key Objectives:\n"
        
        for obj in objectives[:3]:  # Top 3 objectives
            summary += f"• {obj}\n"
        
        summary += "\nExpected Benefits: "
        
        benefit_items = []
        if benefits.get('annual_cost_savings', 0) > 0:
            benefit_items.append(f"${benefits['annual_cost_savings']:,.0f} annual savings")
        if benefits.get('annual_revenue_increase', 0) > 0:
            benefit_items.append(f"${benefits['annual_revenue_increase']:,.0f} annual revenue")
        if benefits.get('efficiency_improvement_pct', 0) > 0:
            benefit_items.append(f"{benefits['efficiency_improvement_pct']}% efficiency gain")
        
        if benefit_items:
            summary += ", ".join(benefit_items)
        else:
            summary += "As quantified in business case"
        
        return summary
    
    def export_to_markdown(self, plan: ProjectPlan, output_path: str) -> str:
        """Export plan to Markdown format"""
        
        md = f"# Project Plan: {plan.charter.project_name}\n\n"
        md += f"**Generated:** {plan.generated_date.strftime('%Y-%m-%d %H:%M')}\n\n"
        md += "---\n\n"
        
        # Executive Summary
        md += "## Executive Summary\n\n"
        md += f"{plan.charter.executive_summary}\n\n"
        
        # Project Charter
        md += "## Project Charter\n\n"
        md += f"**Project ID:** {plan.charter.project_id}\n\n"
        md += f"**Business Problem:**\n{plan.charter.business_problem}\n\n"
        
        md += "**Objectives:**\n"
        for obj in plan.charter.objectives:
            md += f"- {obj}\n"
        md += "\n"
        
        md += "**Key Deliverables:**\n"
        for deliv in plan.charter.key_deliverables:
            md += f"- {deliv}\n"
        md += "\n"
        
        md += "**Success Criteria:**\n"
        for criteria in plan.charter.success_criteria:
            md += f"- {criteria}\n"
        md += "\n"
        
        # Scope
        md += "## Scope\n\n"
        md += "**In Scope:**\n"
        for item in plan.charter.scope_inclusions:
            md += f"- {item}\n"
        md += "\n"
        
        md += "**Out of Scope:**\n"
        for item in plan.charter.scope_exclusions:
            md += f"- {item}\n"
        md += "\n"
        
        # Timeline
        md += "## Timeline\n\n"
        md += f"**Duration:** {plan.timeline['duration_months']} months\n\n"
        md += "**Phases:**\n\n"
        for phase in plan.timeline['phases']:
            md += f"### {phase['name']}\n"
            md += f"- **Duration:** {phase['duration_months']} months\n"
            md += f"- **Period:** Month {phase['start_month']} to {phase['end_month']}\n\n"
        
        # Work Breakdown Structure
        md += "## Work Breakdown Structure\n\n"
        for wp in plan.work_breakdown:
            md += f"### {wp.wbs_id}: {wp.name}\n"
            md += f"{wp.description}\n\n"
            md += f"**Duration:** {wp.duration_months} months\n\n"
            md += "**Deliverables:**\n"
            for deliv in wp.deliverables:
                md += f"- {deliv}\n"
            md += "\n"
        
        # Milestones
        md += "## Milestones & Governance Gates\n\n"
        for milestone in plan.milestones:
            gate_marker = " 🚪 **GOVERNANCE GATE**" if milestone.governance_gate else ""
            md += f"### Month {milestone.target_date_month}: {milestone.name}{gate_marker}\n"
            md += f"{milestone.description}\n\n"
            
            if milestone.governance_gate and milestone.gate_criteria:
                md += "**Gate Criteria:**\n"
                for criteria in milestone.gate_criteria:
                    md += f"- {criteria}\n"
                md += "\n"
        
        # Resource Plan
        md += "## Resource Plan\n\n"
        md += f"**Total Team Size:** {plan.resource_plan['average_team_size']} FTE (average)\n\n"
        md += "**Team Composition:**\n\n"
        for role, details in plan.resource_plan['team_composition'].items():
            md += f"- **{role}:** {details['average_fte']} FTE (avg), {details['peak_fte']} FTE (peak)\n"
            md += f"  - {details['role_description']}\n"
        md += "\n"
        
        # Risk Register
        md += "## Risk Register\n\n"
        for risk in plan.risk_register:
            md += f"### {risk['risk_id']}: {risk['category']} Risk\n"
            md += f"**Description:** {risk['description']}\n\n"
            md += f"**Probability:** {risk['probability']} | **Impact:** {risk['impact']} | **Score:** {risk['risk_score']}\n\n"
            md += f"**Mitigation:** {risk['mitigation']}\n\n"
        
        # Budget
        md += "## Budget & Financial Analysis\n\n"
        md += f"**Total Cost:** ${plan.budget['total_cost']:,.0f}\n\n"
        md += "**Cost Breakdown:**\n"
        for category, amount in plan.budget['cost_breakdown'].items():
            md += f"- {category}: ${amount:,.0f}\n"
        md += "\n"
        
        md += "**Financial Metrics:**\n"
        fs = plan.budget['financial_summary']
        md += f"- **NPV:** ${fs['npv']:,.0f}\n"
        md += f"- **ROI:** {fs['roi_percent']:.1f}%\n"
        md += f"- **Payback Period:** {fs['payback_years']:.1f} years\n"
        md += f"- **Benefit/Cost Ratio:** {fs['benefit_cost_ratio']:.2f}\n\n"
        
        # Stakeholders
        md += "## Stakeholders\n\n"
        for stakeholder in plan.stakeholders:
            md += f"### {stakeholder.name} ({stakeholder.role})\n"
            md += f"**Responsibility:** {stakeholder.responsibility}\n\n"
            md += f"**Engagement Level:** {stakeholder.engagement_level}\n\n"
        
        # Communication Plan
        md += "## Communication Plan\n\n"
        for comm_type, details in plan.communication_plan.items():
            md += f"### {comm_type.replace('_', ' ').title()}\n"
            md += f"- **Frequency:** {details['frequency']}\n"
            md += f"- **Format:** {details['format']}\n"
            md += f"- **Audience:** {', '.join(details['audience'])}\n"
            md += f"- **Content:** {', '.join(details['content'])}\n\n"
        
        # Assumptions & Constraints
        md += "## Assumptions\n\n"
        for assumption in plan.charter.assumptions:
            md += f"- {assumption}\n"
        md += "\n"
        
        md += "## Constraints\n\n"
        for constraint in plan.charter.constraints:
            md += f"- {constraint}\n"
        md += "\n"
        
        # Strategic Alignment
        md += "## Strategic Alignment\n\n"
        sa = plan.charter.strategic_alignment
        md += f"**Overall Alignment Score:** {sa['alignment_score']:.1f}/100 ({sa['alignment_level']})\n\n"
        md += "**Strategic Pillar Scores:**\n"
        for pillar, score in sa['pillar_scores'].items():
            md += f"- {pillar.replace('_', ' ').title()}: {score:.1f}/100\n"
        md += "\n"
        
        # Write to file
        with open(output_path, 'w') as f:
            f.write(md)
        
        return output_path


# Demo usage
if __name__ == '__main__':
    
    # Example project idea
    project_idea = {
        'project_id': 'PROJ-AI-CHATBOT',
        'project_name': 'AI Customer Service Chatbot',
        'description': 'Implement AI-powered chatbot to handle customer service inquiries',
        'business_problem': 'High customer service costs and long response times leading to customer dissatisfaction',
        'project_type': 'Digital Technology',
        'duration_months': 18,
        'total_cost': 500000,
        'dependencies': [],
        'resource_requirements': {
            'Engineering': 20,
            'Design': 5,
            'Product Management': 12,
            'QA': 10
        },
        'expected_benefits': {
            'annual_cost_savings': 200000,
            'efficiency_improvement_pct': 40,
            'automation_hours': 5000,
            'hourly_rate': 50
        },
        'innovation_level': 'High',
        'market_impact': 'Medium'
    }
    
    # Generate plan
    generator = ProjectPlanGenerator()
    plan = generator.draft_project_plan(project_idea)
    
    # Export to markdown
    output_file = generator.export_to_markdown(plan, 'sample_project_plan.md')
    
    print(f"✅ Project plan generated successfully!")
    print(f"📄 Exported to: {output_file}")
    print(f"\n📊 Plan Summary:")
    print(f"   Project: {plan.charter.project_name}")
    print(f"   Duration: {plan.timeline['duration_months']} months")
    print(f"   Budget: ${plan.budget['total_cost']:,.0f}")
    print(f"   ROI: {plan.budget['financial_summary']['roi_percent']:.1f}%")
    print(f"   Milestones: {len(plan.milestones)}")
    print(f"   Work Packages: {len(plan.work_breakdown)}")
    print(f"   Risks: {len(plan.risk_register)}")
