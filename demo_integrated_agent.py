#!/usr/bin/env python3
"""
Demo: Integrated Agent Orchestration

Demonstrates LangGraph agent coordinating all portfolio intelligence features:
- Demand evaluation with intelligent routing
- Benefit monitoring with early warnings
- Sequencing optimization with dependencies
- Location assignment with resource constraints
- Unified agent recommendations

Author: Portfolio ML
Version: 1.0.0
"""

from integrated_agent_orchestrator import create_orchestrator
import json
from datetime import datetime


def demo_integrated_agent():
    """Run complete integrated agent demonstration"""
    
    print("=" * 80)
    print("🤖 INTEGRATED AGENT ORCHESTRATION DEMO")
    print("=" * 80)
    print("\nDemonstrates LangGraph deep agent coordinating ALL portfolio features:")
    print("  ✅ Demand Evaluation")
    print("  ✅ Benefit Intelligence")
    print("  ✅ Sequencing Optimization")
    print("  ✅ Location Resource Optimization")
    print("  ✅ Risk & Cost Prediction (via LangGraph)\n")
    
    # Initialize orchestrator (without API key for demo - uses rule-based fallback)
    print("Initializing agent orchestrator...")
    orchestrator = create_orchestrator(api_key=None)
    print("✅ Agent ready\n")
    
    # Define scenario data
    new_ideas = [
        {
            'project_id': 'IDEA-001',
            'title': 'AI Customer Service Chatbot',
            'description': 'Deploy ML-powered customer support automation',
            'estimated_cost': 500000,
            'estimated_duration_months': 6,
            'strategic_alignment': 90,
            'expected_roi': 250,
            'risk_level': 'MEDIUM',
            'complexity': 'HIGH'
        },
        {
            'project_id': 'IDEA-002',
            'title': 'Legacy System Migration',
            'description': 'Move mainframe to cloud infrastructure',
            'estimated_cost': 2000000,
            'estimated_duration_months': 18,
            'strategic_alignment': 95,
            'expected_roi': 150,
            'risk_level': 'HIGH',
            'complexity': 'VERY_HIGH'
        }
    ]
    
    active_projects = [
        {
            'project_id': 'PROJ-101',
            'duration_months': 8,
            'priority_score': 90,
            'dependencies': [],
            'resource_requirements': {'Engineering': 10, 'Design': 3, 'PM': 2},
            'strategic_value': 95,
            'npv': 1500000,
            'allowed_locations': ['US', 'EU', 'APAC']
        },
        {
            'project_id': 'PROJ-102',
            'duration_months': 6,
            'priority_score': 80,
            'dependencies': ['PROJ-101'],
            'resource_requirements': {'Engineering': 8, 'Design': 2, 'PM': 1},
            'strategic_value': 85,
            'npv': 1200000,
            'allowed_locations': ['US', 'EU']
        },
        {
            'project_id': 'PROJ-103',
            'duration_months': 4,
            'priority_score': 75,
            'dependencies': [],
            'resource_requirements': {'Engineering': 5, 'Design': 2, 'PM': 1},
            'strategic_value': 70,
            'npv': 800000,
            'allowed_locations': ['APAC']
        },
        {
            'project_id': 'PROJ-104',
            'duration_months': 10,
            'priority_score': 85,
            'dependencies': ['PROJ-101'],
            'resource_requirements': {'Engineering': 12, 'Design': 4, 'PM': 2},
            'strategic_value': 90,
            'npv': 1800000,
            'allowed_locations': ['US', 'EU', 'APAC']
        },
        {
            'project_id': 'PROJ-105',
            'duration_months': 5,
            'priority_score': 70,
            'dependencies': ['PROJ-102', 'PROJ-104'],
            'resource_requirements': {'Engineering': 6, 'Design': 1, 'PM': 1},
            'strategic_value': 65,
            'npv': 600000,
            'allowed_locations': ['US', 'APAC']
        }
    ]
    
    location_resources = {
        'US': {
            'Engineering': 50,
            'Design': 15,
            'PM': 10
        },
        'EU': {
            'Engineering': 40,
            'Design': 12,
            'PM': 8
        },
        'APAC': {
            'Engineering': 30,
            'Design': 10,
            'PM': 6
        }
    }
    
    resource_constraints = {
        'Engineering': 100,
        'Design': 30,
        'PM': 20
    }
    
    # Run full orchestration
    print("\n" + "=" * 80)
    print("🚀 STARTING FULL PORTFOLIO ORCHESTRATION")
    print("=" * 80)
    
    result = orchestrator.full_portfolio_orchestration(
        new_ideas=new_ideas,
        active_projects=active_projects,
        location_resources=location_resources,
        resource_constraints=resource_constraints
    )
    
    # Display results
    print("\n" + "=" * 80)
    print("📊 ORCHESTRATION RESULTS")
    print("=" * 80)
    
    # New ideas evaluation
    print("\n📝 NEW IDEAS EVALUATED:")
    print("-" * 80)
    for eval_result in result['new_ideas_evaluated']:
        idea_id = eval_result['evaluation']['project_id']
        routing = eval_result['agent_insights']['routing_decision']
        recommendation = eval_result['agent_insights']['agent_recommendation']
        
        print(f"\n  {idea_id}:")
        print(f"    Routing: {routing}")
        print(f"    Action: {recommendation['action']}")
        print(f"    Reason: {recommendation['reason']}")
        print(f"    Confidence: {recommendation['confidence']:.0%}")
    
    # Active projects monitoring
    print("\n\n📊 ACTIVE PROJECTS MONITORED:")
    print("-" * 80)
    for monitor_result in result['active_projects_monitored']:
        project_id = monitor_result['agent_synthesis']['project_id']
        health = monitor_result['agent_synthesis']['health_status']
        actions = monitor_result['agent_synthesis']['agent_actions']
        
        print(f"\n  {project_id}:")
        print(f"    Health: {health}")
        if actions:
            print(f"    Actions:")
            for action in actions:
                print(f"      • {action['action']}: {action['reason']}")
    
    # Sequencing optimization
    if result['sequencing_optimized']:
        print("\n\n📅 SEQUENCING OPTIMIZATION:")
        print("-" * 80)
        seq_result = result['sequencing_optimized']['sequencing_result']
        agent_analysis = result['sequencing_optimized']['agent_analysis']
        
        print(f"\n  Status: {seq_result['status']}")
        print(f"  Total Duration: {seq_result['total_duration_months']} months")
        print(f"  Critical Path: {' → '.join(seq_result['critical_path'])}")
        print(f"  Execution Phases: {len(seq_result['execution_phases'])}")
        
        print("\n  Agent Recommendations:")
        for rec in agent_analysis['agent_recommendations']:
            print(f"    • [{rec['type']}] {rec.get('recommendation', rec.get('insight'))}")
    
    # Location assignment
    if result['locations_assigned']:
        print("\n\n🌍 LOCATION ASSIGNMENTS:")
        print("-" * 80)
        loc_result = result['locations_assigned']['location_result']
        agent_analysis = result['locations_assigned']['agent_analysis']
        
        print(f"\n  Status: {loc_result['status']}")
        print(f"  Projects Selected: {loc_result['projects_selected']}/{loc_result['total_projects']}")
        print(f"  Total NPV: ${loc_result['total_value']:,.0f}")
        
        print("\n  Projects by Location:")
        for location, projects in loc_result['projects_by_location'].items():
            print(f"    {location}: {projects}")
        
        print("\n  Agent Insights:")
        for insight in agent_analysis['agent_recommendations']:
            if insight['type'] == 'LOCATION_INSIGHT':
                print(f"    • {insight['recommendation']}")
    
    # Master recommendations
    print("\n\n💡 MASTER RECOMMENDATIONS:")
    print("-" * 80)
    for rec in result['master_recommendations']:
        priority = rec['priority']
        rec_type = rec['type']
        recommendation = rec['recommendation']
        
        emoji = {'HIGH': '🔴', 'CRITICAL': '⚠️', 'MEDIUM': '🟡'}.get(priority, '⚪')
        print(f"\n  {emoji} [{priority}] {rec_type}")
        print(f"    {recommendation}")
    
    print("\n\n" + "=" * 80)
    print("✅ ORCHESTRATION COMPLETE")
    print("=" * 80)
    
    # Summary statistics
    print("\n📈 SUMMARY STATISTICS:")
    print("-" * 80)
    print(f"  New Ideas Evaluated: {len(result['new_ideas_evaluated'])}")
    print(f"  Active Projects Monitored: {len(result['active_projects_monitored'])}")
    print(f"  Master Recommendations: {len(result['master_recommendations'])}")
    print(f"  Orchestration Time: {result['orchestrated_at']}")
    
    return result


if __name__ == "__main__":
    try:
        result = demo_integrated_agent()
        print("\n✅ Demo completed successfully")
        exit(0)
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
