#!/usr/bin/env python3
"""
AI Agent Portfolio Orchestrator UI

Interactive web interface for the LangGraph-powered portfolio intelligence agent.

Features:
- Real-time agent orchestration dashboard
- Idea evaluation with confidence scores
- Project health monitoring
- Sequencing optimization visualization
- Location assignment analysis
- Master recommendations feed

Author: Portfolio ML
Version: 1.0.0
"""

import streamlit as st
from integrated_agent_orchestrator import create_orchestrator
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="AI Portfolio Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .recommendation-high {
        background-color: #ffebee;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #f44336;
        margin-bottom: 0.5rem;
    }
    .recommendation-critical {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff9800;
        margin-bottom: 0.5rem;
    }
    .recommendation-medium {
        background-color: #fff9c4;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #fdd835;
        margin-bottom: 0.5rem;
    }
    .agent-thinking {
        background-color: #e3f2fd;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-style: italic;
        color: #1976d2;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = None
if 'orchestration_result' not in st.session_state:
    st.session_state.orchestration_result = None
if 'ideas' not in st.session_state:
    st.session_state.ideas = []
if 'projects' not in st.session_state:
    st.session_state.projects = []

# Header
st.markdown('<div class="main-header">🤖 AI Portfolio Agent Orchestrator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">LangGraph-Powered Autonomous Portfolio Intelligence</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Key input
    api_key = st.text_input(
        "OpenAI API Key (Optional)",
        type="password",
        help="Leave empty to use rule-based fallback"
    )
    
    # Initialize orchestrator
    if st.button("🚀 Initialize Agent", use_container_width=True):
        with st.spinner("Initializing AI agent..."):
            st.session_state.orchestrator = create_orchestrator(
                api_key=api_key if api_key else None
            )
            st.success("✅ Agent ready!")
    
    st.divider()
    
    # Agent status
    if st.session_state.orchestrator:
        st.success("🟢 Agent: Active")
        st.info(f"Mode: {'LLM-powered' if api_key else 'Rule-based'}")
    else:
        st.warning("🟡 Agent: Not initialized")
    
    st.divider()
    
    # Quick actions
    st.header("🎯 Quick Actions")
    
    if st.button("📝 Load Sample Ideas", use_container_width=True):
        st.session_state.ideas = [
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
        st.success("Loaded 2 sample ideas")
    
    if st.button("📊 Load Sample Projects", use_container_width=True):
        st.session_state.projects = [
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
            }
        ]
        st.success("Loaded 3 sample projects")

# Main content
if not st.session_state.orchestrator:
    st.info("👈 Initialize the agent from the sidebar to begin")
    st.stop()

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🎯 Orchestration Dashboard",
    "📝 Idea Evaluation",
    "📊 Project Monitoring",
    "⚙️ Configuration",
    "📋 Draft Project Plan",
    "👥 Team Recommendations"
])

# Tab 1: Orchestration Dashboard
with tab1:
    st.header("Full Portfolio Orchestration")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Run Agent Orchestration")
        st.markdown("Agent will evaluate ideas, monitor projects, optimize sequencing, and assign locations.")
    
    with col2:
        if st.button("🚀 Run Full Orchestration", use_container_width=True, type="primary"):
            if not st.session_state.ideas and not st.session_state.projects:
                st.error("Please load sample data first from the sidebar")
            else:
                with st.spinner("🤖 Agent is thinking..."):
                    location_resources = {
                        'US': {'Engineering': 50, 'Design': 15, 'PM': 10},
                        'EU': {'Engineering': 40, 'Design': 12, 'PM': 8},
                        'APAC': {'Engineering': 30, 'Design': 10, 'PM': 6}
                    }
                    
                    resource_constraints = {
                        'Engineering': 100,
                        'Design': 30,
                        'PM': 20
                    }
                    
                    result = st.session_state.orchestrator.full_portfolio_orchestration(
                        new_ideas=st.session_state.ideas,
                        active_projects=st.session_state.projects,
                        location_resources=location_resources,
                        resource_constraints=resource_constraints
                    )
                    
                    st.session_state.orchestration_result = result
                    st.success("✅ Orchestration complete!")
    
    st.divider()
    
    # Display results
    if st.session_state.orchestration_result:
        result = st.session_state.orchestration_result
        
        # Key metrics
        st.markdown("### 📊 Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Ideas Evaluated",
                len(result.get('new_ideas_evaluated', [])),
                help="Number of new ideas evaluated by agent"
            )
        
        with col2:
            st.metric(
                "Projects Monitored",
                len(result.get('active_projects_monitored', [])),
                help="Number of active projects monitored"
            )
        
        with col3:
            critical_count = sum(
                1 for r in result.get('master_recommendations', [])
                if r.get('priority') == 'CRITICAL'
            )
            st.metric(
                "Critical Items",
                critical_count,
                delta="Needs attention" if critical_count > 0 else None,
                delta_color="inverse"
            )
        
        with col4:
            st.metric(
                "Total Recommendations",
                len(result.get('master_recommendations', [])),
                help="Total recommendations from agent"
            )
        
        st.divider()
        
        # Master Recommendations
        st.markdown("### 💡 Master Recommendations")
        st.markdown("**Agent-prioritized actions for executive review:**")
        
        for rec in result.get('master_recommendations', []):
            priority = rec.get('priority', 'MEDIUM')
            rec_type = rec.get('type', 'GENERAL')
            recommendation = rec.get('recommendation', 'No details')
            
            if priority == 'CRITICAL':
                emoji = "⚠️"
                css_class = "recommendation-critical"
            elif priority == 'HIGH':
                emoji = "🔴"
                css_class = "recommendation-high"
            else:
                emoji = "🟡"
                css_class = "recommendation-medium"
            
            st.markdown(f"""
            <div class="{css_class}">
                <strong>{emoji} [{priority}] {rec_type}</strong><br>
                {recommendation}
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Idea Evaluation Results
        if result.get('new_ideas_evaluated'):
            st.markdown("### 📝 Idea Evaluations")
            
            for eval_result in result['new_ideas_evaluated']:
                eval_data = eval_result.get('evaluation', {})
                agent_insights = eval_result.get('agent_insights', {})
                recommendation = agent_insights.get('agent_recommendation', {})
                
                with st.expander(f"💡 {eval_data.get('project_id', 'Unknown')}: {recommendation.get('action', 'N/A')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Evaluation:**")
                        st.write(f"Routing: `{agent_insights.get('routing_decision', 'N/A')}`")
                        st.write(f"Priority: `{agent_insights.get('priority_tier', 'N/A')}`")
                    
                    with col2:
                        st.markdown("**Agent Recommendation:**")
                        st.write(f"Action: `{recommendation.get('action', 'N/A')}`")
                        st.write(f"Confidence: `{recommendation.get('confidence', 0):.0%}`")
                    
                    st.markdown(f"**Reasoning:** {recommendation.get('reason', 'N/A')}")
        
        # Project Monitoring Results
        if result.get('active_projects_monitored'):
            st.markdown("### 📊 Project Health Monitoring")
            
            health_data = []
            for monitor_result in result['active_projects_monitored']:
                synthesis = monitor_result.get('agent_synthesis', {})
                health_data.append({
                    'Project': synthesis.get('project_id', 'Unknown'),
                    'Health': synthesis.get('health_status', 'UNKNOWN'),
                    'Actions': len(synthesis.get('agent_actions', []))
                })
            
            if health_data:
                df = pd.DataFrame(health_data)
                
                # Color coding for health status
                def color_health(val):
                    if val == 'HEALTHY':
                        return 'background-color: #c8e6c9'
                    elif val == 'AT_RISK':
                        return 'background-color: #fff9c4'
                    elif val == 'CRITICAL':
                        return 'background-color: #ffcdd2'
                    return ''
                
                st.dataframe(
                    df.style.applymap(color_health, subset=['Health']),
                    use_container_width=True
                )
        
        # Sequencing Results
        if result.get('sequencing_optimized'):
            st.markdown("### 📅 Sequencing Optimization")
            
            seq_result = result['sequencing_optimized'].get('sequencing_result', {})
            agent_analysis = result['sequencing_optimized'].get('agent_analysis', {})
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Duration", f"{seq_result.get('total_duration_months', 0)} months")
            
            with col2:
                st.metric("Execution Phases", len(seq_result.get('execution_phases', [])))
            
            with col3:
                st.metric("Critical Path Length", len(seq_result.get('critical_path', [])))
            
            st.markdown(f"**Critical Path:** {' → '.join(seq_result.get('critical_path', []))}")
            
            # Agent recommendations
            for rec in agent_analysis.get('agent_recommendations', []):
                st.info(f"**{rec.get('type', 'INSIGHT')}:** {rec.get('recommendation', rec.get('insight', 'N/A'))}")
        
        # Location Assignment Results
        if result.get('locations_assigned'):
            st.markdown("### 🌍 Location Assignments")
            
            loc_result = result['locations_assigned'].get('location_result', {})
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Projects Selected", f"{loc_result.get('projects_selected', 0)}/{loc_result.get('total_projects', 0)}")
            
            with col2:
                st.metric("Total NPV", f"${loc_result.get('total_value', 0):,.0f}")
            
            with col3:
                st.metric("Status", loc_result.get('status', 'UNKNOWN'))
            
            # Location distribution chart
            projects_by_location = loc_result.get('projects_by_location', {})
            if projects_by_location:
                fig = go.Figure(data=[
                    go.Bar(
                        x=list(projects_by_location.keys()),
                        y=[len(v) for v in projects_by_location.values()],
                        text=[len(v) for v in projects_by_location.values()],
                        textposition='auto',
                        marker_color=['#1f77b4', '#ff7f0e', '#2ca02c']
                    )
                ])
                fig.update_layout(
                    title="Projects by Location",
                    xaxis_title="Location",
                    yaxis_title="Number of Projects",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

# Tab 2: Idea Evaluation
with tab2:
    st.header("Evaluate New Ideas")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Add New Idea")
        
        with st.form("new_idea_form"):
            idea_id = st.text_input("Project ID", value=f"IDEA-{datetime.now().strftime('%Y%m%d%H%M%S')}")
            title = st.text_input("Title", placeholder="AI Customer Service Chatbot")
            description = st.text_area("Description", placeholder="Deploy ML-powered customer support...")
            
            col_a, col_b = st.columns(2)
            with col_a:
                cost = st.number_input("Estimated Cost ($)", min_value=0, value=500000, step=10000)
                duration = st.number_input("Duration (months)", min_value=1, value=6, step=1)
            
            with col_b:
                alignment = st.slider("Strategic Alignment", 0, 100, 75)
                roi = st.number_input("Expected ROI (%)", min_value=0, value=150, step=10)
            
            risk = st.selectbox("Risk Level", ["LOW", "MEDIUM", "HIGH", "CRITICAL"])
            complexity = st.selectbox("Complexity", ["LOW", "MEDIUM", "HIGH", "VERY_HIGH"])
            
            submitted = st.form_submit_button("🤖 Evaluate with Agent", use_container_width=True)
            
            if submitted:
                idea = {
                    'project_id': idea_id,
                    'title': title,
                    'description': description,
                    'estimated_cost': cost,
                    'estimated_duration_months': duration,
                    'strategic_alignment': alignment,
                    'expected_roi': roi,
                    'risk_level': risk,
                    'complexity': complexity
                }
                
                with st.spinner("🤖 Agent is evaluating..."):
                    result = st.session_state.orchestrator.autonomous_idea_evaluation(idea)
                    
                    st.session_state.ideas.append(idea)
                    
                    # Display results
                    st.success("✅ Evaluation complete!")
                    
                    agent_insights = result.get('agent_insights', {})
                    recommendation = agent_insights.get('agent_recommendation', {})
                    
                    st.markdown(f"""
                    <div class="agent-thinking">
                        🤖 Agent Decision: <strong>{recommendation.get('action', 'N/A')}</strong>
                        (Confidence: {recommendation.get('confidence', 0):.0%})
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.info(f"**Reasoning:** {recommendation.get('reason', 'N/A')}")
    
    with col2:
        st.markdown("### Current Ideas")
        st.metric("Total Ideas", len(st.session_state.ideas))
        
        for idea in st.session_state.ideas:
            st.markdown(f"**{idea['project_id']}**")
            st.caption(idea['title'])

# Tab 3: Project Monitoring
with tab3:
    st.header("Monitor Project Health")
    
    if st.session_state.projects:
        st.markdown("### Active Projects")
        
        project_df = pd.DataFrame([
            {
                'Project ID': p['project_id'],
                'Duration': f"{p['duration_months']} mo",
                'Priority': p['priority_score'],
                'Strategic Value': p['strategic_value'],
                'NPV': f"${p['npv']:,.0f}"
            }
            for p in st.session_state.projects
        ])
        
        st.dataframe(project_df, use_container_width=True)
        
        # Select project to monitor
        selected_project = st.selectbox(
            "Select project to monitor",
            [p['project_id'] for p in st.session_state.projects]
        )
        
        if st.button("🤖 Monitor with Agent", use_container_width=True):
            with st.spinner("🤖 Agent is analyzing..."):
                result = st.session_state.orchestrator.autonomous_benefit_monitoring(selected_project)
                
                synthesis = result.get('agent_synthesis', {})
                health = synthesis.get('health_status', 'UNKNOWN')
                actions = synthesis.get('agent_actions', [])
                
                # Display health status
                if health == 'HEALTHY':
                    st.success(f"✅ Health Status: **{health}**")
                elif health == 'AT_RISK':
                    st.warning(f"⚠️ Health Status: **{health}**")
                else:
                    st.error(f"🔴 Health Status: **{health}**")
                
                # Display actions
                if actions:
                    st.markdown("### Agent Recommended Actions")
                    for action in actions:
                        st.info(f"**{action.get('action', 'N/A')}:** {action.get('reason', 'N/A')}")
    else:
        st.info("Load sample projects from the sidebar to begin monitoring")

# Tab 4: Configuration
with tab4:
    st.header("Agent Configuration")
    
    st.markdown("### Location Resources")
    st.markdown("Configure resource capacity at each location:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🇺🇸 US**")
        us_eng = st.number_input("Engineering", value=50, key="us_eng")
        us_design = st.number_input("Design", value=15, key="us_design")
        us_pm = st.number_input("PM", value=10, key="us_pm")
    
    with col2:
        st.markdown("**🇪🇺 EU**")
        eu_eng = st.number_input("Engineering", value=40, key="eu_eng")
        eu_design = st.number_input("Design", value=12, key="eu_design")
        eu_pm = st.number_input("PM", value=8, key="eu_pm")
    
    with col3:
        st.markdown("**🌏 APAC**")
        apac_eng = st.number_input("Engineering", value=30, key="apac_eng")
        apac_design = st.number_input("Design", value=10, key="apac_design")
        apac_pm = st.number_input("PM", value=6, key="apac_pm")
    
    st.divider()
    
    st.markdown("### Resource Constraints")
    st.markdown("Global portfolio constraints:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        constraint_eng = st.number_input("Max Engineering", value=100, key="constraint_eng")
    
    with col2:
        constraint_design = st.number_input("Max Design", value=30, key="constraint_design")
    
    with col3:
        constraint_pm = st.number_input("Max PM", value=20, key="constraint_pm")

# Tab 5: Draft Project Plan
with tab5:
    st.header("Generate Project Plan")
    st.markdown("Auto-generate comprehensive project plans in < 5 minutes")
    
    with st.form("plan_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            project_id = st.text_input("Project ID", value="PROJ-NEW-001")
            project_name = st.text_input("Project Name", value="New Project")
            project_type = st.selectbox(
                "Project Type",
                ["Digital Technology", "Operational", "Strategic", "Innovation"]
            )
            duration = st.number_input("Duration (months)", value=12, min_value=1)
            total_cost = st.number_input("Total Cost ($)", value=500000, min_value=0, step=50000)
        
        with col2:
            description = st.text_area("Description", height=100)
            business_problem = st.text_area("Business Problem", height=100)
            expected_savings = st.number_input("Expected Annual Savings ($)", value=200000, min_value=0, step=10000)
            efficiency_gain = st.number_input("Efficiency Improvement (%)", value=30, min_value=0, max_value=100)
        
        submitted = st.form_submit_button("🚀 Generate Plan", use_container_width=True, type="primary")
    
    if submitted:
        with st.spinner("🤖 Agent is generating your project plan..."):
            from project_plan_generator import ProjectPlanGenerator
            
            project_idea = {
                'project_id': project_id,
                'project_name': project_name,
                'description': description,
                'business_problem': business_problem,
                'project_type': project_type,
                'duration_months': duration,
                'total_cost': total_cost,
                'dependencies': [],
                'resource_requirements': {
                    'Engineering': duration * 2,
                    'Design': duration * 0.5,
                    'Product Management': duration * 1
                },
                'expected_benefits': {
                    'annual_cost_savings': expected_savings,
                    'efficiency_improvement_pct': efficiency_gain
                }
            }
            
            generator = ProjectPlanGenerator()
            plan = generator.draft_project_plan(project_idea)
            
            # Store in session state
            st.session_state.generated_plan = plan
            
            st.success("✅ Project plan generated successfully!")
    
    # Display generated plan
    if 'generated_plan' in st.session_state:
        plan = st.session_state.generated_plan
        
        st.divider()
        st.markdown("### 📊 Plan Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Duration", f"{plan.timeline['duration_months']} months")
        with col2:
            st.metric("Budget", f"${plan.budget['total_cost']:,.0f}")
        with col3:
            st.metric("ROI", f"{plan.budget['financial_summary']['roi_percent']:.1f}%")
        with col4:
            st.metric("Milestones", len(plan.milestones))
        
        st.divider()
        
        # Expanders for plan details
        with st.expander("📋 Executive Summary", expanded=True):
            st.write(plan.charter.executive_summary)
        
        with st.expander("🎯 Objectives"):
            for obj in plan.charter.objectives:
                st.write(f"• {obj}")
        
        with st.expander("📅 Timeline & Phases"):
            for phase in plan.timeline['phases']:
                st.write(f"**{phase['name']}**: {phase['duration_months']} months (Month {phase['start_month']}-{phase['end_month']})")        
        with st.expander("⚠️ Risk Register"):
            for risk in plan.risk_register[:5]:
                st.write(f"**{risk['risk_id']}** - {risk['category']}: Score {risk['risk_score']}/100")
                st.caption(risk['description'])
        
        with st.expander("💰 Budget Breakdown"):
            for category, amount in plan.budget['cost_breakdown'].items():
                st.write(f"• {category}: ${amount:,.0f}")
        
        st.divider()
        
        # Export options
        st.markdown("### 📥 Export Plan")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Export Markdown", use_container_width=True):
                output_file = generator.export_to_markdown(plan, f"{project_id}_plan.md")
                st.success(f"Exported to {output_file}")
        
        with col2:
            if st.button("📄 Export PDF", use_container_width=True):
                try:
                    from report_templates import ReportExporter
                    exporter = ReportExporter()
                    output_file = exporter.export_to_pdf(plan, f"{project_id}_plan.pdf")
                    st.success(f"Exported to {output_file}")
                except Exception as e:
                    st.warning("PDF export requires: pip install reportlab")
        
        with col3:
            if st.button("📄 Export Word", use_container_width=True):
                try:
                    from report_templates import ReportExporter
                    exporter = ReportExporter()
                    output_file = exporter.export_to_word(plan, f"{project_id}_plan.docx")
                    st.success(f"Exported to {output_file}")
                except Exception as e:
                    st.warning("Word export requires: pip install python-docx")

# Tab 6: Team Recommendations
with tab6:
    st.header("AI Team Recommendations")
    st.markdown("Get optimal team composition in < 2 minutes")
    
    with st.form("team_form"):
        st.markdown("### Project Requirements")
        col1, col2 = st.columns(2)
        
        with col1:
            complexity = st.selectbox(
                "Project Complexity",
                ["HIGH", "MEDIUM", "LOW"]
            )
            team_duration = st.number_input("Duration (months)", value=12, min_value=1)
            optimization = st.selectbox(
                "Optimization Objective",
                ["balanced", "cost", "quality"]
            )
        
        with col2:
            st.markdown("**Required Skills** (one per line)")
            skills_input = st.text_area(
                "Skills",
                value="Python\nMachine Learning\nAPI Development",
                height=100,
                label_visibility="collapsed"
            )
        
        submitted_team = st.form_submit_button("🎯 Get Recommendations", use_container_width=True, type="primary")
    
    if submitted_team:
        with st.spinner("🤖 Agent is analyzing team composition..."):
            from team_recommender import (
                TeamRecommender, Person, Skill, SkillLevel, SeniorityLevel
            )
            
            # Parse skills
            skills_list = [s.strip() for s in skills_input.split('\n') if s.strip()]
            required_skills = [
                {'skill': skill, 'level': 'Advanced'}
                for skill in skills_list
            ]
            
            project_reqs = {
                'required_skills': required_skills,
                'duration_months': team_duration,
                'project_complexity': complexity,
                'project_type': 'Digital Technology'
            }
            
            # Sample people (in real app, load from database)
            people = [
                Person(
                    person_id='P001',
                    name='Jane Smith',
                    role='Tech Lead',
                    seniority=SeniorityLevel.SENIOR,
                    skills=[
                        Skill('Python', SkillLevel.EXPERT, 8),
                        Skill('Machine Learning', SkillLevel.ADVANCED, 6),
                        Skill('API Development', SkillLevel.EXPERT, 7)
                    ],
                    location='US',
                    current_utilization=40,
                    cost_per_month=15000,
                    performance_score=92,
                    project_history=['PROJ-001', 'PROJ-005']
                ),
                Person(
                    person_id='P002',
                    name='John Doe',
                    role='Senior Engineer',
                    seniority=SeniorityLevel.SENIOR,
                    skills=[
                        Skill('Python', SkillLevel.ADVANCED, 5),
                        Skill('React', SkillLevel.EXPERT, 6),
                        Skill('Database Design', SkillLevel.ADVANCED, 5)
                    ],
                    location='US',
                    current_utilization=60,
                    cost_per_month=12000,
                    performance_score=88,
                    project_history=['PROJ-003', 'PROJ-008']
                ),
                Person(
                    person_id='P003',
                    name='Alice Chen',
                    role='Engineer',
                    seniority=SeniorityLevel.MID_LEVEL,
                    skills=[
                        Skill('Python', SkillLevel.ADVANCED, 3),
                        Skill('Machine Learning', SkillLevel.INTERMEDIATE, 2),
                        Skill('API Development', SkillLevel.INTERMEDIATE, 3)
                    ],
                    location='APAC',
                    current_utilization=30,
                    cost_per_month=8000,
                    performance_score=85,
                    project_history=['PROJ-010']
                )
            ]
            
            recommender = TeamRecommender()
            recommendations = recommender.recommend_team(
                project_reqs,
                people,
                optimization_objective=optimization
            )
            
            # Store in session state
            st.session_state.team_recommendations = recommendations
            
            st.success("✅ Team recommendations generated!")
    
    # Display recommendations
    if 'team_recommendations' in st.session_state:
        recommendations = st.session_state.team_recommendations
        
        for i, rec in enumerate(recommendations):
            if i == 0:
                st.markdown("### 🏆 PRIMARY RECOMMENDATION")
            else:
                opt_type = "Cost-Optimized" if i == 1 else "Quality-Optimized"
                st.markdown(f"### 💡 ALTERNATIVE {i}: {opt_type}")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Skill Match", f"{rec.overall_skill_match:.1f}%")
            with col2:
                st.metric("Team Size", f"{rec.team_size_fte:.1f} FTE")
            with col3:
                st.metric("Total Cost", f"${rec.total_cost:,.0f}")
            with col4:
                st.metric("Performance", f"{rec.predicted_performance:.1f}/100")
            
            st.markdown(f"**Confidence:** {rec.confidence:.1f}%")
            
            with st.expander("👥 Team Members", expanded=(i==0)):
                for member in rec.team_members:
                    st.markdown(f"**{member.person.name}** ({member.person.role})")
                    st.write(f"Allocation: {member.allocation*100:.0f}% | Skill Match: {member.skill_match_score:.0f}%")
                    st.caption(f"Rationale: {member.rationale}")
                    st.divider()
            
            if rec.strengths:
                with st.expander("✅ Strengths"):
                    for strength in rec.strengths:
                        st.write(f"• {strength}")
            
            if rec.risk_factors:
                with st.expander("⚠️ Risk Factors"):
                    for risk in rec.risk_factors:
                        st.write(f"• {risk}")
            
            if rec.skill_gaps:
                with st.expander("🔴 Skill Gaps"):
                    for gap in rec.skill_gaps:
                        st.write(f"• {gap}")
            
            st.divider()
        
        # Export team report
        st.markdown("### 📥 Export Team Report")
        if st.button("📄 Export Report", use_container_width=True):
            from report_templates import ReportExporter
            exporter = ReportExporter()
            output_file = exporter.export_team_report(
                recommendations[0],
                "team_recommendation_report.md"
            )
            st.success(f"Exported to {output_file}")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <strong>AI Portfolio Agent Orchestrator</strong> | 
    Powered by LangGraph | 
    Portfolio ML v1.0.0
</div>
""", unsafe_allow_html=True)
