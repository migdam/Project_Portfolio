#!/usr/bin/env python3
"""
Project Planning Suite - Complete Demo

Demonstrates all Project Planning Suite capabilities:
1. Auto-generate comprehensive project plans
2. AI-powered team recommendations
3. Integration with existing portfolio modules

Author: Portfolio ML
Version: 1.0.0
"""

from project_plan_generator import ProjectPlanGenerator
from team_recommender import (
    TeamRecommender, Person, Skill, SkillLevel, SeniorityLevel
)


def demo_project_plan_generation():
    """Demo: Auto-generate a comprehensive project plan"""
    
    print("=" * 80)
    print("DEMO 1: AUTO-GENERATE PROJECT PLAN")
    print("=" * 80)
    print()
    
    # Define project idea
    project_idea = {
        'project_id': 'PROJ-ECOMMERCE-2025',
        'project_name': 'E-Commerce Platform Modernization',
        'description': 'Modernize legacy e-commerce platform with cloud-native architecture',
        'business_problem': 'Current platform cannot scale, has frequent outages, high maintenance costs',
        'project_type': 'Digital Technology',
        'duration_months': 24,
        'total_cost': 2_500_000,
        'dependencies': [],
        'resource_requirements': {
            'Engineering': 48,
            'Design': 12,
            'Product Management': 18,
            'QA': 16,
            'DevOps': 10
        },
        'expected_benefits': {
            'annual_revenue_increase': 5_000_000,
            'annual_cost_savings': 800_000,
            'efficiency_improvement_pct': 60,
            'automation_hours': 20000,
            'hourly_rate': 75
        },
        'innovation_level': 'High',
        'market_impact': 'High',
        'project_complexity': 'HIGH'
    }
    
    print("📋 Generating project plan...")
    print(f"   Project: {project_idea['project_name']}")
    print(f"   Duration: {project_idea['duration_months']} months")
    print(f"   Budget: ${project_idea['total_cost']:,.0f}")
    print()
    
    # Generate plan
    generator = ProjectPlanGenerator()
    plan = generator.draft_project_plan(project_idea)
    
    # Display results
    print("✅ PROJECT PLAN GENERATED")
    print()
    print("📊 PLAN SUMMARY:")
    print(f"   Project ID: {plan.charter.project_id}")
    print(f"   Duration: {plan.timeline['duration_months']} months")
    print(f"   Budget: ${plan.budget['total_cost']:,.0f}")
    print(f"   NPV: ${plan.budget['financial_summary']['npv']:,.0f}")
    print(f"   ROI: {plan.budget['financial_summary']['roi_percent']:.1f}%")
    print(f"   Payback: {plan.budget['financial_summary']['payback_years']:.1f} years")
    print()
    
    print("📋 PLAN CONTENTS:")
    print(f"   ✅ Executive Summary: {len(plan.charter.executive_summary)} chars")
    print(f"   ✅ Objectives: {len(plan.charter.objectives)}")
    print(f"   ✅ Key Deliverables: {len(plan.charter.key_deliverables)}")
    print(f"   ✅ Success Criteria: {len(plan.charter.success_criteria)}")
    print(f"   ✅ Phases: {len(plan.timeline['phases'])}")
    print(f"   ✅ Work Packages: {len(plan.work_breakdown)}")
    print(f"   ✅ Milestones: {len(plan.milestones)}")
    print(f"   ✅ Governance Gates: {sum(1 for m in plan.milestones if m.governance_gate)}")
    print(f"   ✅ Risks: {len(plan.risk_register)}")
    print(f"   ✅ Stakeholders: {len(plan.stakeholders)}")
    print()
    
    print("📈 STRATEGIC ALIGNMENT:")
    sa = plan.charter.strategic_alignment
    print(f"   Overall Score: {sa['alignment_score']:.1f}/100 ({sa['alignment_level']})")
    print("   Pillar Scores:")
    for pillar, score in sa['pillar_scores'].items():
        pillar_name = pillar.replace('_', ' ').title()
        print(f"     • {pillar_name}: {score:.1f}/100")
    print()
    
    print("⚠️  TOP 3 RISKS:")
    for i, risk in enumerate(plan.risk_register[:3], 1):
        print(f"   {i}. [{risk['risk_id']}] {risk['category']}")
        print(f"      Score: {risk['risk_score']}/100 | {risk['probability']}/{risk['impact']}")
        print(f"      {risk['description'][:70]}...")
    print()
    
    print("🎯 MILESTONES WITH GOVERNANCE GATES:")
    gate_milestones = [m for m in plan.milestones if m.governance_gate]
    for milestone in gate_milestones[:3]:
        print(f"   🚪 Month {milestone.target_date_month}: {milestone.name}")
        if milestone.gate_criteria:
            print(f"      Criteria: {milestone.gate_criteria[0]}")
    print()
    
    # Export to markdown
    output_file = generator.export_to_markdown(
        plan, 
        'demo_ecommerce_project_plan.md'
    )
    print(f"📄 Exported to: {output_file}")
    print()
    
    return plan


def demo_team_recommendations():
    """Demo: AI-powered team recommendations"""
    
    print("=" * 80)
    print("DEMO 2: AI-POWERED TEAM RECOMMENDATIONS")
    print("=" * 80)
    print()
    
    # Define available people
    people = [
        Person(
            person_id='P001',
            name='Sarah Chen',
            role='Senior Architect',
            seniority=SeniorityLevel.PRINCIPAL,
            skills=[
                Skill('Cloud Architecture', SkillLevel.EXPERT, 12),
                Skill('Microservices', SkillLevel.EXPERT, 10),
                Skill('Python', SkillLevel.ADVANCED, 8),
                Skill('Kubernetes', SkillLevel.EXPERT, 7)
            ],
            location='US',
            current_utilization=50,
            cost_per_month=18_000,
            performance_score=95,
            project_history=['PROJ-001', 'PROJ-005', 'PROJ-012', 'PROJ-018']
        ),
        Person(
            person_id='P002',
            name='Marcus Johnson',
            role='Tech Lead',
            seniority=SeniorityLevel.SENIOR,
            skills=[
                Skill('Python', SkillLevel.EXPERT, 10),
                Skill('Java', SkillLevel.ADVANCED, 8),
                Skill('React', SkillLevel.ADVANCED, 6),
                Skill('Database Design', SkillLevel.EXPERT, 9)
            ],
            location='US',
            current_utilization=40,
            cost_per_month=15_000,
            performance_score=92,
            project_history=['PROJ-003', 'PROJ-008', 'PROJ-015']
        ),
        Person(
            person_id='P003',
            name='Priya Sharma',
            role='Senior Engineer',
            seniority=SeniorityLevel.SENIOR,
            skills=[
                Skill('React', SkillLevel.EXPERT, 7),
                Skill('Node.js', SkillLevel.EXPERT, 6),
                Skill('TypeScript', SkillLevel.ADVANCED, 5),
                Skill('UI/UX', SkillLevel.ADVANCED, 6)
            ],
            location='APAC',
            current_utilization=30,
            cost_per_month=10_000,
            performance_score=90,
            project_history=['PROJ-010', 'PROJ-016']
        ),
        Person(
            person_id='P004',
            name='David Kim',
            role='DevOps Lead',
            seniority=SeniorityLevel.SENIOR,
            skills=[
                Skill('Kubernetes', SkillLevel.EXPERT, 8),
                Skill('CI/CD', SkillLevel.EXPERT, 9),
                Skill('AWS', SkillLevel.EXPERT, 10),
                Skill('Terraform', SkillLevel.ADVANCED, 6)
            ],
            location='US',
            current_utilization=60,
            cost_per_month=16_000,
            performance_score=93,
            project_history=['PROJ-002', 'PROJ-007', 'PROJ-013']
        ),
        Person(
            person_id='P005',
            name='Elena Rodriguez',
            role='Senior QA Engineer',
            seniority=SeniorityLevel.SENIOR,
            skills=[
                Skill('Test Automation', SkillLevel.EXPERT, 8),
                Skill('Python', SkillLevel.ADVANCED, 6),
                Skill('Selenium', SkillLevel.EXPERT, 7),
                Skill('Performance Testing', SkillLevel.ADVANCED, 5)
            ],
            location='EU',
            current_utilization=45,
            cost_per_month=12_000,
            performance_score=88,
            project_history=['PROJ-004', 'PROJ-011']
        ),
        Person(
            person_id='P006',
            name='Alex Turner',
            role='Mid-Level Engineer',
            seniority=SeniorityLevel.MID_LEVEL,
            skills=[
                Skill('Python', SkillLevel.ADVANCED, 4),
                Skill('React', SkillLevel.INTERMEDIATE, 3),
                Skill('Database Design', SkillLevel.INTERMEDIATE, 3)
            ],
            location='US',
            current_utilization=25,
            cost_per_month=9_000,
            performance_score=82,
            project_history=['PROJ-014']
        ),
        Person(
            person_id='P007',
            name='Yuki Tanaka',
            role='Engineer',
            seniority=SeniorityLevel.MID_LEVEL,
            skills=[
                Skill('Java', SkillLevel.ADVANCED, 5),
                Skill('Microservices', SkillLevel.INTERMEDIATE, 3),
                Skill('Kubernetes', SkillLevel.INTERMEDIATE, 2)
            ],
            location='APAC',
            current_utilization=20,
            cost_per_month=8_000,
            performance_score=85,
            project_history=['PROJ-009']
        )
    ]
    
    # Project requirements
    project_reqs = {
        'required_skills': [
            {'skill': 'Cloud Architecture', 'level': 'Advanced'},
            {'skill': 'Microservices', 'level': 'Advanced'},
            {'skill': 'Python', 'level': 'Advanced'},
            {'skill': 'React', 'level': 'Advanced'},
            {'skill': 'Kubernetes', 'level': 'Intermediate'},
            {'skill': 'CI/CD', 'level': 'Advanced'},
            {'skill': 'Database Design', 'level': 'Advanced'},
            {'skill': 'Test Automation', 'level': 'Advanced'}
        ],
        'duration_months': 24,
        'project_complexity': 'HIGH',
        'project_type': 'Digital Technology'
    }
    
    print("🎯 Finding optimal team composition...")
    print(f"   Project Complexity: {project_reqs['project_complexity']}")
    print(f"   Duration: {project_reqs['duration_months']} months")
    print(f"   Required Skills: {len(project_reqs['required_skills'])}")
    print(f"   Available People: {len(people)}")
    print()
    
    # Get recommendations
    recommender = TeamRecommender()
    recommendations = recommender.recommend_team(
        project_reqs,
        people,
        optimization_objective='balanced'
    )
    
    # Display results
    for i, rec in enumerate(recommendations):
        if i == 0:
            print("🏆 PRIMARY RECOMMENDATION (Balanced)")
        else:
            obj = "Cost-Optimized" if i == 1 else "Quality-Optimized"
            print(f"\n💡 ALTERNATIVE {i} ({obj})")
        
        print("=" * 80)
        print(f"Skill Match: {rec.overall_skill_match:.1f}%")
        print(f"Team Size: {rec.team_size_fte:.1f} FTE")
        print(f"Total Cost: ${rec.total_cost:,.0f}")
        print(f"Predicted Performance: {rec.predicted_performance:.1f}/100")
        print(f"Confidence: {rec.confidence:.1f}%")
        print()
        
        print("👥 TEAM COMPOSITION:")
        for member in rec.team_members:
            util = member.person.current_utilization
            new_util = util + (member.allocation * 100)
            print(f"   • {member.person.name} ({member.person.role})")
            print(f"     Allocation: {member.allocation*100:.0f}% | Skill Match: {member.skill_match_score:.0f}%")
            print(f"     Utilization: {util:.0f}% → {new_util:.0f}%")
            print(f"     Cost: ${member.person.cost_per_month * member.allocation:,.0f}/month")
            print(f"     Rationale: {member.rationale}")
        print()
        
        if rec.strengths:
            print("✅ STRENGTHS:")
            for strength in rec.strengths:
                print(f"   • {strength}")
            print()
        
        if rec.risk_factors:
            print("⚠️  RISK FACTORS:")
            for risk in rec.risk_factors:
                print(f"   • {risk}")
            print()
        
        if rec.skill_gaps:
            print("🔴 SKILL GAPS:")
            for gap in rec.skill_gaps:
                print(f"   • {gap}")
            print()
    
    return recommendations


def demo_integrated_workflow():
    """Demo: Integrated plan + team workflow"""
    
    print("=" * 80)
    print("DEMO 3: INTEGRATED WORKFLOW (PLAN + TEAM)")
    print("=" * 80)
    print()
    
    print("📋 Step 1: Generate project plan...")
    plan = demo_project_plan_generation()
    
    print("\n")
    print("👥 Step 2: Recommend team based on plan requirements...")
    
    # Extract requirements from plan
    resource_requirements = plan.resource_plan['team_composition']
    
    print(f"   Plan requires {plan.resource_plan['average_team_size']} FTE average")
    print(f"   Resource breakdown:")
    for role, details in list(resource_requirements.items())[:3]:
        print(f"     • {role}: {details['average_fte']} FTE")
    print()
    
    recommendations = demo_team_recommendations()
    
    print("\n")
    print("=" * 80)
    print("🎉 INTEGRATED WORKFLOW COMPLETE")
    print("=" * 80)
    print()
    print("📊 SUMMARY:")
    print(f"   ✅ Project Plan: {plan.charter.project_name}")
    print(f"   ✅ Duration: {plan.timeline['duration_months']} months")
    print(f"   ✅ Budget: ${plan.budget['total_cost']:,.0f}")
    print(f"   ✅ ROI: {plan.budget['financial_summary']['roi_percent']:.1f}%")
    print(f"   ✅ Team Size: {recommendations[0].team_size_fte:.1f} FTE")
    print(f"   ✅ Team Cost: ${recommendations[0].total_cost:,.0f}")
    print(f"   ✅ Skill Match: {recommendations[0].overall_skill_match:.1f}%")
    print(f"   ✅ Predicted Performance: {recommendations[0].predicted_performance:.1f}/100")
    print()
    print("💡 Next Steps:")
    print("   1. Review project plan: demo_ecommerce_project_plan.md")
    print("   2. Present team recommendations to stakeholders")
    print("   3. Secure approval and resources")
    print("   4. Execute with monitoring and benefit tracking")
    print()


if __name__ == '__main__':
    import sys
    
    print("\n")
    print("🎯 PROJECT PLANNING SUITE - COMPLETE DEMO")
    print("=" * 80)
    print()
    print("This demo showcases:")
    print("  1. Auto-generate comprehensive project plans (< 5 minutes)")
    print("  2. AI-powered team recommendations (< 2 minutes)")
    print("  3. Integrated workflow combining both capabilities")
    print()
    print("Choose demo:")
    print("  1 - Project Plan Generation")
    print("  2 - Team Recommendations")
    print("  3 - Integrated Workflow (Plan + Team)")
    print("  0 - Run All Demos")
    print()
    
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        choice = input("Enter choice (0-3): ").strip()
    
    print()
    
    if choice == '1':
        demo_project_plan_generation()
    elif choice == '2':
        demo_team_recommendations()
    elif choice == '3':
        demo_integrated_workflow()
    else:
        # Run all demos
        demo_project_plan_generation()
        print("\n" * 2)
        demo_team_recommendations()
        print("\n" * 2)
        print("=" * 80)
        print("✅ ALL DEMOS COMPLETE")
        print("=" * 80)
        print()
        print("📄 Files Generated:")
        print("   • demo_ecommerce_project_plan.md - Full project plan")
        print()
        print("📚 To run specific demos:")
        print("   python demo_project_planning_suite.py 1  # Plan generation")
        print("   python demo_project_planning_suite.py 2  # Team recommendations")
        print("   python demo_project_planning_suite.py 3  # Integrated workflow")
        print()
