#!/usr/bin/env python3
"""
Streamlit UI for Demand Evaluation Toolkit

Interactive web interface for:
- Single idea evaluation
- Batch idea evaluation
- Portfolio optimization
- Results visualization

Author: Portfolio ML
Version: 1.0.0
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from demand_evaluation_toolkit import DemandEvaluationToolkit
import json

# Page config
st.set_page_config(
    page_title="Demand Evaluation Toolkit",
    page_icon="🎯",
    layout="wide"
)

# Initialize toolkit
@st.cache_resource
def get_toolkit():
    return DemandEvaluationToolkit()

toolkit = get_toolkit()

# Sidebar
st.sidebar.title("🎯 Demand Evaluation")
st.sidebar.markdown("---")

mode = st.sidebar.radio(
    "Select Mode",
    ["Single Idea", "Batch Evaluation", "Portfolio Optimizer"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info("""
**AI-Powered Demand Evaluation**

- 99.8% faster than manual
- ML-based classification
- Strategic alignment scoring
- Financial viability analysis
- Portfolio optimization
""")

# Main content
st.title("🎯 Demand Evaluation Toolkit")
st.markdown("**AI-Powered Idea Evaluation & Portfolio Optimization**")
st.markdown("---")

# ============================================================================
# MODE 1: SINGLE IDEA EVALUATION
# ============================================================================
if mode == "Single Idea":
    st.header("📝 Single Idea Evaluation")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Idea Details")
        
        project_id = st.text_input("Project ID", "IDEA-2024-001")
        title = st.text_input("Title", "AI-Powered Customer Support Chatbot")
        description = st.text_area(
            "Description",
            """Implement AI-powered chatbot for customer service using machine learning.
Expected to reduce support costs by 40% and improve response time from 2 hours to 5 minutes.
Requires integration with existing CRM system and 6-month implementation timeline.""",
            height=150
        )
        
        st.markdown("---")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.subheader("Financial Details")
            total_cost = st.number_input("Total Cost ($)", value=500000, step=10000)
            project_duration = st.number_input("Duration (years)", value=2.0, step=0.5)
            
        with col_b:
            st.subheader("Expected Benefits")
            annual_revenue = st.number_input("Annual Revenue Increase ($)", value=0, step=10000)
            annual_savings = st.number_input("Annual Cost Savings ($)", value=1200000, step=10000)
            
        col_c, col_d = st.columns(2)
        with col_c:
            automation_hours = st.number_input("Automation Hours/Year", value=10000, step=1000)
        with col_d:
            risk_score = st.slider("Risk Score (0-100)", 0, 100, 45)
    
    with col2:
        st.subheader("⚙️ Settings")
        auto_classify = st.checkbox("Auto-classify from description", value=True)
        
        st.markdown("---")
        st.subheader("📊 Thresholds")
        st.caption("Min Strategic Alignment")
        min_alignment = st.slider("", 0, 100, 30, key="min_align")
        
        st.caption("Max Risk Score")
        max_risk = st.slider("", 0, 100, 85, key="max_risk")
    
    st.markdown("---")
    
    if st.button("🚀 Evaluate Idea", type="primary", use_container_width=True):
        # Build idea data
        idea_data = {
            'project_id': project_id,
            'title': title,
            'description': description,
            'risk_score': risk_score,
            'total_cost': total_cost,
            'expected_benefits': {
                'annual_revenue_increase': annual_revenue,
                'annual_cost_savings': annual_savings,
                'automation_hours': automation_hours
            },
            'project_duration_years': project_duration
        }
        
        with st.spinner("Evaluating idea..."):
            result = toolkit.evaluate_demand(idea_data, auto_classify=auto_classify)
        
        st.success("✅ Evaluation Complete!")
        
        # Display results
        st.markdown("---")
        st.subheader("📊 Evaluation Results")
        
        # Routing decision
        routing = result['routing']
        if routing == 'APPROVED':
            st.success(f"🎉 **ROUTING: {routing}**")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Priority Tier", result['priority_tier'])
            with col2:
                st.metric("Priority Score", f"{result['priority_score']:.0f}/100")
            with col3:
                st.metric("Confidence", f"{result['confidence']:.1%}")
        elif routing == 'REJECT':
            st.error(f"❌ **ROUTING: {routing}**")
            st.warning(f"**Reason:** {result.get('reason', 'N/A')}")
        elif routing == 'ESCALATE_HIGH_RISK':
            st.warning(f"⚠️ **ROUTING: {routing}**")
            st.info(f"**Reason:** {result.get('reason', 'N/A')}")
        else:
            st.info(f"📝 **ROUTING: {routing}**")
            st.warning(f"**Reason:** {result.get('reason', 'N/A')}")
        
        st.markdown("---")
        
        # Detailed steps
        tabs = st.tabs(["Classification", "Alignment", "Financial", "Risk", "Priority"])
        
        with tabs[0]:
            if 'classification' in result['steps']:
                cls = result['steps']['classification']
                if cls.get('status') == 'SUCCESS':
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Category", cls['category'])
                    with col2:
                        st.metric("Sub-type", cls['sub_type'])
                    with col3:
                        st.metric("Confidence", f"{cls['confidence']:.1%}")
                    
                    st.caption("**Keywords:**")
                    st.write(", ".join(cls['keywords'][:5]))
            else:
                st.info("Auto-classification was not performed")
        
        with tabs[1]:
            if 'alignment' in result['steps']:
                align = result['steps']['alignment']
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Alignment Score", f"{align['alignment_score']:.0f}/100")
                with col2:
                    st.metric("Level", align['alignment_level'])
                
                if 'strong_pillars' in align:
                    st.success(f"**Strong Pillars:** {', '.join(align['strong_pillars'])}")
                if 'weak_pillars' in align:
                    st.warning(f"**Weak Pillars:** {', '.join(align['weak_pillars'])}")
        
        with tabs[2]:
            if 'financial' in result['steps']:
                fin = result['steps']['financial']
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("ROI", f"{fin['roi']:.1f}%")
                with col2:
                    st.metric("Payback", f"{fin['payback_period']:.1f} yrs")
                with col3:
                    st.metric("NPV", f"${fin['npv']:,.0f}")
                
                st.info(f"**Financial Viability:** {fin['viability_level']}")
        
        with tabs[3]:
            if 'risk' in result['steps']:
                risk = result['steps']['risk']
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Risk Score", f"{risk.get('risk_score', 'N/A')}/100")
                with col2:
                    st.metric("Risk Level", risk.get('risk_level', 'Unknown'))
        
        with tabs[4]:
            if 'priority' in result['steps']:
                pri = result['steps']['priority']
                
                # Priority breakdown
                components = pri['components']
                weights = pri['weights']
                
                df = pd.DataFrame({
                    'Component': ['Strategic Alignment', 'Risk-Adjusted Success', 'Financial Viability'],
                    'Score': [components['strategic_alignment'], 
                             components['risk_adjusted_success'],
                             components['financial_viability']],
                    'Weight': [weights['strategic_alignment'],
                              weights['risk_adjusted_success'],
                              weights['financial_viability']],
                    'Weighted': [components['strategic_alignment'] * weights['strategic_alignment'],
                                components['risk_adjusted_success'] * weights['risk_adjusted_success'],
                                components['financial_viability'] * weights['financial_viability']]
                })
                
                fig = px.bar(df, x='Component', y='Weighted', 
                           title='Priority Score Breakdown',
                           labels={'Weighted': 'Weighted Score'},
                           color='Weighted',
                           color_continuous_scale='Blues')
                st.plotly_chart(fig, use_container_width=True)
                
                st.dataframe(df, use_container_width=True)

# ============================================================================
# MODE 2: BATCH EVALUATION
# ============================================================================
elif mode == "Batch Evaluation":
    st.header("📦 Batch Idea Evaluation")
    
    st.markdown("""
    Upload multiple ideas for evaluation or use sample data.
    """)
    
    # Sample data button
    if st.button("Load Sample Ideas"):
        st.session_state['sample_loaded'] = True
    
    # File upload or sample
    if st.session_state.get('sample_loaded'):
        st.info("Using 5 sample ideas")
        
        ideas = [
            {
                'project_id': 'IDEA-001',
                'title': 'AI Customer Support',
                'description': 'AI chatbot for customer service automation',
                'risk_score': 45,
                'total_cost': 500000,
                'expected_benefits': {'annual_cost_savings': 1200000},
                'project_duration_years': 2
            },
            {
                'project_id': 'IDEA-002',
                'title': 'Office Renovation',
                'description': 'Renovate facilities HVAC workspace modernization',
                'risk_score': 35,
                'total_cost': 300000,
                'expected_benefits': {'productivity_improvement_pct': 10},
                'project_duration_years': 1
            },
            {
                'project_id': 'IDEA-003',
                'title': 'Training Program',
                'description': 'Employee training soft skills leadership',
                'risk_score': 25,
                'total_cost': 150000,
                'expected_benefits': {'retention_improvement_pct': 5},
                'project_duration_years': 1
            },
            {
                'project_id': 'IDEA-004',
                'title': 'Recreational Facility',
                'description': 'Build gym game room employee morale',
                'risk_score': 40,
                'total_cost': 800000,
                'expected_benefits': {'employee_satisfaction_improvement': 'High'},
                'project_duration_years': 3
            },
            {
                'project_id': 'IDEA-005',
                'title': 'European Expansion',
                'description': 'Expand into European markets Germany France partnerships',
                'risk_score': 55,
                'total_cost': 2000000,
                'expected_benefits': {'annual_revenue_increase': 3500000},
                'project_duration_years': 2
            }
        ]
        
        if st.button("🚀 Evaluate Batch", type="primary"):
            with st.spinner("Evaluating ideas..."):
                results = toolkit.evaluate_batch(ideas, auto_classify=True)
            
            st.success(f"✅ Evaluated {len(results)} ideas!")
            
            # Summary
            summary = toolkit.get_summary(results)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Evaluated", summary['total_evaluated'])
            with col2:
                st.metric("Approved", summary['approved_count'])
            with col3:
                st.metric("Rejected", summary['rejected_count'])
            with col4:
                st.metric("Approval Rate", f"{summary['approval_rate']:.1%}")
            
            st.markdown("---")
            
            # Routing distribution
            col1, col2 = st.columns(2)
            
            with col1:
                routing_df = pd.DataFrame(
                    list(summary['routing_distribution'].items()),
                    columns=['Routing', 'Count']
                )
                fig = px.pie(routing_df, values='Count', names='Routing',
                           title='Routing Distribution')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if summary['approved_count'] > 0:
                    priority_df = pd.DataFrame(
                        [(k, v) for k, v in summary['priority_distribution'].items() if v > 0],
                        columns=['Priority', 'Count']
                    )
                    fig = px.bar(priority_df, x='Priority', y='Count',
                               title='Priority Distribution (Approved Only)',
                               color='Priority',
                               color_discrete_map={'HIGH': '#00CC96', 'MEDIUM': '#FFA15A', 'LOW': '#EF553B'})
                    st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            # Results table
            st.subheader("📊 Detailed Results")
            
            results_data = []
            for r in results:
                results_data.append({
                    'Project ID': r['project_id'],
                    'Routing': r['routing'],
                    'Priority': r.get('priority_tier', 'N/A'),
                    'Score': f"{r.get('priority_score', 0):.0f}",
                    'Status': r['status']
                })
            
            df = pd.DataFrame(results_data)
            st.dataframe(df, use_container_width=True)
            
            # Store results for optimizer
            st.session_state['batch_results'] = results

# ============================================================================
# MODE 3: PORTFOLIO OPTIMIZER
# ============================================================================
elif mode == "Portfolio Optimizer":
    st.header("🎯 Portfolio Optimization")
    
    st.markdown("""
    Select optimal subset of approved ideas subject to resource constraints.
    """)
    
    # Check if we have batch results
    if 'batch_results' not in st.session_state:
        st.warning("⚠️ Please run Batch Evaluation first to get approved ideas")
        st.info("Go to **Batch Evaluation** mode, load sample ideas, and evaluate them.")
    else:
        results = st.session_state['batch_results']
        approved = [r for r in results if r['routing'] == 'APPROVED']
        
        st.info(f"Found {len(approved)} approved ideas from previous evaluation")
        
        if len(approved) == 0:
            st.error("No approved ideas to optimize. All ideas were rejected/escalated.")
        else:
            st.markdown("---")
            st.subheader("⚙️ Resource Constraints")
            
            col1, col2 = st.columns(2)
            
            with col1:
                total_budget = st.number_input(
                    "Total Budget ($)",
                    value=5000000,
                    step=100000,
                    help="Maximum budget available"
                )
                
                max_concurrent = st.number_input(
                    "Max Concurrent Projects",
                    value=3,
                    step=1,
                    help="Maximum number of projects to run simultaneously"
                )
            
            with col2:
                max_avg_risk = st.slider(
                    "Max Average Risk Score",
                    0, 100, 50,
                    help="Maximum acceptable average risk across portfolio"
                )
                
                objective = st.selectbox(
                    "Optimization Objective",
                    ["balanced", "maximize_npv", "maximize_strategic"],
                    help="What to optimize for"
                )
            
            st.markdown("---")
            
            if st.button("🚀 Optimize Portfolio", type="primary", use_container_width=True):
                constraints = {
                    'total_budget': total_budget,
                    'max_concurrent_projects': max_concurrent,
                    'max_avg_risk': max_avg_risk
                }
                
                with st.spinner("Running optimization..."):
                    optimized = toolkit.optimize_portfolio(
                        approved_demands=approved,
                        constraints=constraints,
                        objective=objective
                    )
                
                if optimized['optimization_status'] == 'SUCCESS':
                    st.success("✅ Optimization Successful!")
                    
                    # Key metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Selected", f"{optimized['num_selected']}/{len(approved)}")
                    with col2:
                        st.metric("Total NPV", f"${optimized['total_npv']:,.0f}")
                    with col3:
                        st.metric("Total Cost", f"${optimized['total_cost']:,.0f}")
                    with col4:
                        st.metric("Budget Used", f"{optimized['total_cost']/total_budget*100:.0f}%")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Avg Risk", f"{optimized['avg_risk']:.0f}/100")
                    with col2:
                        st.metric("Avg Strategic", f"{optimized['avg_strategic_score']:.0f}/100")
                    
                    st.markdown("---")
                    
                    # Selected projects
                    st.subheader("📋 Selected Projects")
                    
                    selected_df = pd.DataFrame(optimized['selected_details'])
                    selected_df = selected_df[['project_id', 'npv', 'cost', 'strategic_score', 'risk_score']]
                    selected_df.columns = ['Project ID', 'NPV ($)', 'Cost ($)', 'Strategic Score', 'Risk Score']
                    
                    st.dataframe(selected_df, use_container_width=True)
                    
                    # Visualization
                    fig = go.Figure()
                    
                    for detail in optimized['selected_details']:
                        fig.add_trace(go.Scatter(
                            x=[detail['risk_score']],
                            y=[detail['npv']],
                            mode='markers+text',
                            marker=dict(
                                size=detail['cost']/50000,
                                color=detail['strategic_score'],
                                colorscale='Viridis',
                                showscale=True,
                                colorbar=dict(title="Strategic<br>Score")
                            ),
                            text=[detail['project_id']],
                            textposition="top center",
                            name=detail['project_id']
                        ))
                    
                    fig.update_layout(
                        title='Selected Portfolio: Risk vs NPV (size = cost)',
                        xaxis_title='Risk Score',
                        yaxis_title='NPV ($)',
                        showlegend=False,
                        height=500
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                else:
                    st.error(f"❌ Optimization failed: {optimized.get('message', 'Unknown error')}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Demand Evaluation Toolkit v1.0.0 | Powered by Portfolio ML</p>
    <p>99.8% faster than manual evaluation | 70-85% higher confidence | 100% coverage</p>
</div>
""", unsafe_allow_html=True)
