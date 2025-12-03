"""Demo Streamlit Dashboard for Screenshots"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="Portfolio ML Dashboard",
    page_icon="🎯",
    layout="wide"
)

# Header
st.title("🎯 Portfolio ML Dashboard")
st.markdown("### AI-Powered Project & Portfolio Machine Learning")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Controls")
    st.markdown("**Model Selection**")
    selected_model = st.selectbox("Choose Model", ["PRM - Risk", "COP - Cost", "SLM - Success", "PO - Optimizer"])
    
    st.markdown("**Filters**")
    risk_filter = st.multiselect("Risk Level", ["LOW", "MEDIUM", "HIGH"], default=["MEDIUM", "HIGH"])
    
    st.markdown("**Model Status** ✅")
    st.metric("PRM Accuracy", "89%", "+2.1%")
    st.metric("COP R² Score", "82%", "+1.5%")
    st.metric("SLM AUC-ROC", "91%", "0.0%")
    
    st.markdown("---")
    st.markdown("**System Health**")
    st.success("All models operational")
    st.info("No drift detected")

# Main content
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Projects", "247", "+12")
with col2:
    st.metric("High Risk", "34", "-5")
with col3:
    st.metric("Avg Success Rate", "85.3%", "+3.2%")
with col4:
    st.metric("Portfolio Value", "$45.2M", "+8.1%")

st.markdown("---")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Risk Analysis", "💰 Cost Predictions", "✅ Success Likelihood", "🎯 Portfolio Optimizer"])

with tab1:
    st.subheader("Project Risk Predictions")
    
    # Sample data
    risk_data = pd.DataFrame({
        'Project': [f'PROJ-{i:03d}' for i in range(1, 26)],
        'Risk Score': np.random.randint(20, 95, 25),
        'Confidence': np.random.uniform(0.75, 0.95, 25),
        'Budget (M)': np.random.uniform(0.5, 5.0, 25),
        'Status': np.random.choice(['Active', 'Planning', 'At Risk'], 25)
    })
    risk_data['Risk Level'] = risk_data['Risk Score'].apply(
        lambda x: 'HIGH' if x > 70 else 'MEDIUM' if x > 40 else 'LOW'
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Risk distribution
        fig = px.scatter(risk_data, 
                        x='Risk Score', 
                        y='Budget (M)',
                        size='Confidence',
                        color='Risk Level',
                        hover_data=['Project', 'Status'],
                        title='Risk Score vs Budget',
                        color_discrete_map={'LOW': 'green', 'MEDIUM': 'orange', 'HIGH': 'red'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Risk level distribution
        risk_counts = risk_data['Risk Level'].value_counts()
        fig2 = go.Figure(data=[go.Pie(labels=risk_counts.index, values=risk_counts.values,
                                       marker_colors=['red', 'orange', 'green'])])
        fig2.update_layout(title='Risk Distribution')
        st.plotly_chart(fig2, use_container_width=True)
    
    # Top risk projects
    st.markdown("#### 🚨 Top 10 High-Risk Projects")
    top_risk = risk_data.nlargest(10, 'Risk Score')[['Project', 'Risk Score', 'Risk Level', 'Confidence', 'Status']]
    st.dataframe(top_risk, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Cost Overrun Predictions")
    
    # Sample cost data
    cost_data = pd.DataFrame({
        'Project': [f'PROJ-{i:03d}' for i in range(1, 21)],
        'Original Budget (M)': np.random.uniform(1.0, 10.0, 20),
        'Predicted Overrun %': np.random.uniform(-5, 25, 20),
        'Confidence': np.random.uniform(0.70, 0.92, 20)
    })
    cost_data['Predicted Final (M)'] = cost_data['Original Budget (M)'] * (1 + cost_data['Predicted Overrun %']/100)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(cost_data.head(15), 
                    x='Project', 
                    y='Predicted Overrun %',
                    color='Predicted Overrun %',
                    color_continuous_scale=['green', 'yellow', 'red'],
                    title='Predicted Cost Overruns')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig2 = px.scatter(cost_data,
                         x='Original Budget (M)',
                         y='Predicted Final (M)',
                         size='Confidence',
                         hover_data=['Project'],
                         title='Budget vs Predicted Final Cost')
        fig2.add_trace(go.Scatter(x=[0, 10], y=[0, 10], mode='lines', name='No Overrun Line', line=dict(dash='dash')))
        st.plotly_chart(fig2, use_container_width=True)

with tab3:
    st.subheader("Project Success Likelihood")
    
    # Sample success data
    success_data = pd.DataFrame({
        'Project': [f'PROJ-{i:03d}' for i in range(1, 21)],
        'Success Probability': np.random.uniform(0.45, 0.98, 20),
        'Team Experience': np.random.randint(1, 10, 20),
        'Duration (months)': np.random.randint(6, 36, 20)
    })
    success_data['Category'] = success_data['Success Probability'].apply(
        lambda x: 'High' if x > 0.8 else 'Medium' if x > 0.6 else 'Low'
    )
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        fig = px.scatter(success_data,
                        x='Duration (months)',
                        y='Success Probability',
                        size='Team Experience',
                        color='Category',
                        hover_data=['Project'],
                        title='Success Probability vs Project Duration',
                        color_discrete_map={'High': 'green', 'Medium': 'orange', 'Low': 'red'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        avg_success = success_data['Success Probability'].mean()
        st.metric("Average Success Rate", f"{avg_success*100:.1f}%")
        
        category_counts = success_data['Category'].value_counts()
        st.markdown("**By Category:**")
        for cat in ['High', 'Medium', 'Low']:
            if cat in category_counts.index:
                st.write(f"{cat}: {category_counts[cat]} projects")

with tab4:
    st.subheader("Portfolio Optimization")
    
    # Pareto frontier
    portfolio_data = pd.DataFrame({
        'Project': [f'PROJ-{i:03d}' for i in range(1, 31)],
        'Strategic Value': np.random.randint(40, 100, 30),
        'Risk Score': np.random.randint(20, 90, 30),
        'NPV (M)': np.random.uniform(0.5, 8.0, 30)
    })
    portfolio_data['Selected'] = portfolio_data.apply(
        lambda row: 'Optimal' if row['Strategic Value'] > 70 and row['Risk Score'] < 50 else 'Candidate',
        axis=1
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = px.scatter(portfolio_data,
                        x='Risk Score',
                        y='Strategic Value',
                        size='NPV (M)',
                        color='Selected',
                        hover_data=['Project'],
                        title='Portfolio Optimization: Pareto Frontier',
                        color_discrete_map={'Optimal': 'gold', 'Candidate': 'lightblue'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**Optimization Results**")
        optimal_count = len(portfolio_data[portfolio_data['Selected'] == 'Optimal'])
        st.metric("Optimal Projects", optimal_count)
        st.metric("Total Portfolio Value", f"${portfolio_data[portfolio_data['Selected']=='Optimal']['NPV (M)'].sum():.1f}M")
        st.metric("Avg Risk Score", f"{portfolio_data[portfolio_data['Selected']=='Optimal']['Risk Score'].mean():.0f}")
        
        st.markdown("**Recommendations:**")
        st.success(f"✅ {optimal_count} projects in optimal zone")
        st.warning(f"⚠️ {30-optimal_count} projects need review")

st.markdown("---")
st.markdown("#### 📈 Model Performance Trends")

# Performance timeline
dates = pd.date_range(start='2025-10-01', end='2025-12-03', freq='W')
perf_data = pd.DataFrame({
    'Date': dates,
    'PRM Accuracy': np.random.uniform(0.85, 0.91, len(dates)),
    'COP R² Score': np.random.uniform(0.78, 0.84, len(dates)),
    'SLM AUC-ROC': np.random.uniform(0.88, 0.93, len(dates))
})

fig = go.Figure()
fig.add_trace(go.Scatter(x=perf_data['Date'], y=perf_data['PRM Accuracy'], name='PRM', mode='lines+markers'))
fig.add_trace(go.Scatter(x=perf_data['Date'], y=perf_data['COP R² Score'], name='COP', mode='lines+markers'))
fig.add_trace(go.Scatter(x=perf_data['Date'], y=perf_data['SLM AUC-ROC'], name='SLM', mode='lines+markers'))
fig.update_layout(title='Model Performance Over Time', yaxis_title='Score', hovermode='x unified')
st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("**Portfolio ML System** | Version 1.0.0 | Last Updated: 2025-12-03")
