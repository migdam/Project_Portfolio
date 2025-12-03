"""Real-Time Portfolio Tracking Dashboard with SQLite Persistence"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time
from database import PortfolioDB

# Page configuration
st.set_page_config(
    page_title="Portfolio ML - Real-Time Tracking",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
@st.cache_resource
def get_database():
    return PortfolioDB("portfolio_predictions.db")

db = get_database()

# Header
st.title("📊 Portfolio ML - Real-Time Tracking Dashboard")
st.markdown("### Live monitoring with SQLite persistence - All data is saved!")

# Sidebar controls
with st.sidebar:
    st.header("⚙️ Dashboard Controls")
    
    auto_refresh = st.checkbox("Auto-refresh (every 5s)", value=False)
    
    st.markdown("---")
    st.header("📊 Database Stats")
    
    stats = db.get_statistics()
    st.metric("Total Predictions", f"{stats['total_predictions']:,}")
    st.metric("Today's Predictions", f"{stats['predictions_today']:,}")
    st.metric("Unique Projects", stats['unique_projects'])
    st.metric("Avg Risk (24h)", f"{stats['avg_risk_24h']:.1f}")
    st.metric("High Risk (24h)", stats['high_risk_count_24h'])
    
    st.markdown("---")
    st.header("📈 Model Status")
    
    # Model health indicators
    models = {
        "PRM": {"status": "✅", "accuracy": 89},
        "COP": {"status": "✅", "accuracy": 82},
        "SLM": {"status": "✅", "accuracy": 91},
        "PO": {"status": "✅", "accuracy": 87}
    }
    
    for model, info in models.items():
        st.metric(f"{info['status']} {model}", f"{info['accuracy']}%")
    
    st.markdown("---")
    
    if st.button("🔄 Generate New Prediction"):
        # Generate and store new prediction
        project_id = f"PROJ-{np.random.randint(1, 50):03d}"
        risk_score = int(np.random.randint(20, 90))
        cost_variance = float(np.random.uniform(-5, 25))
        success_prob = float(np.random.uniform(0.5, 0.95))
        
        db.store_prediction(
            project_id=project_id,
            risk_score=risk_score,
            cost_variance=cost_variance,
            success_probability=success_prob,
            priority_score=int(70 + np.random.randint(0, 30))
        )
        
        # Log activity
        severity = "HIGH" if risk_score > 70 else "MEDIUM" if risk_score > 40 else "LOW"
        db.log_activity(
            event_type="PREDICTION",
            description=f"Risk: {risk_score}, Cost: {cost_variance:.1f}%",
            project_id=project_id,
            severity=severity
        )
        
        st.success(f"✅ Predicted {project_id}")
        st.rerun()
    
    if st.button("🗑️ Cleanup Old Data (>90 days)"):
        result = db.cleanup_old_data(days=90)
        st.info(f"Cleaned: {result['predictions_deleted']} predictions")
    
    if st.button("📥 Export to CSV"):
        db.export_to_csv("predictions", "predictions_export.csv")
        st.success("✅ Exported to predictions_export.csv")

# Fetch data from database
predictions_24h = db.get_predictions(hours=24, limit=1000)
df_predictions = pd.DataFrame(predictions_24h) if predictions_24h else pd.DataFrame()

# Top metrics row
if not df_predictions.empty:
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("24h Predictions", len(df_predictions))
    
    with col2:
        avg_risk = df_predictions['risk_score'].mean()
        st.metric("Avg Risk Score", f"{avg_risk:.1f}")
    
    with col3:
        high_risk_count = len(df_predictions[df_predictions['risk_score'] > 70])
        st.metric("High Risk Projects", high_risk_count)
    
    with col4:
        avg_cost = df_predictions['cost_variance'].mean()
        color = "🟢" if avg_cost < 10 else "🟡" if avg_cost < 15 else "🔴"
        st.metric("Avg Cost Variance", f"{color} {avg_cost:.1f}%")
    
    with col5:
        unique_projects = df_predictions['project_id'].nunique()
        st.metric("Projects Analyzed", unique_projects)
    
    st.markdown("---")
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Risk Timeline",
        "💰 Cost Analysis",
        "📊 Project Trends",
        "🔔 Activity Log"
    ])
    
    with tab1:
        st.subheader("Risk Score Timeline - Last 24 Hours")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Convert timestamp strings to datetime
            df_plot = df_predictions.copy()
            df_plot['timestamp'] = pd.to_datetime(df_plot['timestamp'])
            
            # Scatter plot with color coding
            fig = px.scatter(
                df_plot.tail(100),
                x='timestamp',
                y='risk_score',
                color='risk_score',
                color_continuous_scale=['green', 'yellow', 'orange', 'red'],
                size=[8]*min(100, len(df_plot)),
                hover_data=['project_id', 'cost_variance'],
                title="Project Risk Scores Over Time"
            )
            
            # Add risk zones
            fig.add_hrect(y0=0, y1=30, fillcolor="green", opacity=0.1, line_width=0)
            fig.add_hrect(y0=30, y1=60, fillcolor="yellow", opacity=0.1, line_width=0)
            fig.add_hrect(y0=60, y1=80, fillcolor="orange", opacity=0.1, line_width=0)
            fig.add_hrect(y0=80, y1=100, fillcolor="red", opacity=0.1, line_width=0)
            
            fig.update_layout(height=400, xaxis_title="Time", yaxis_title="Risk Score")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 🎯 Risk Distribution")
            low = len(df_predictions[df_predictions['risk_score'] < 30])
            medium = len(df_predictions[(df_predictions['risk_score'] >= 30) & (df_predictions['risk_score'] < 60)])
            high = len(df_predictions[(df_predictions['risk_score'] >= 60) & (df_predictions['risk_score'] < 80)])
            critical = len(df_predictions[df_predictions['risk_score'] >= 80])
            
            st.metric("🟢 Low (0-30)", low)
            st.metric("🟡 Medium (30-60)", medium)
            st.metric("🟠 High (60-80)", high)
            st.metric("🔴 Critical (80+)", critical)
            
            # Pie chart
            fig_pie = go.Figure(data=[go.Pie(
                labels=['Low', 'Medium', 'High', 'Critical'],
                values=[low, medium, high, critical],
                marker_colors=['green', 'yellow', 'orange', 'red']
            )])
            fig_pie.update_layout(height=250, showlegend=False)
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with tab2:
        st.subheader("Cost Variance Analysis")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Bar chart with color coding
            df_cost = df_predictions.tail(50).copy()
            df_cost['timestamp'] = pd.to_datetime(df_cost['timestamp'])
            colors = ['green' if v < 5 else 'yellow' if v < 15 else 'red' 
                     for v in df_cost['cost_variance']]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df_cost['project_id'],
                y=df_cost['cost_variance'],
                marker_color=colors,
                hovertext=df_cost['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
            ))
            
            fig.add_hline(y=0, line_color="gray", line_width=1)
            fig.add_hline(y=15, line_dash="dash", line_color="red",
                         annotation_text="Critical: 15%")
            
            fig.update_layout(
                title="Cost Variance by Project (Last 50)",
                xaxis_title="Project ID",
                yaxis_title="Variance (%)",
                height=400,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 💰 Variance Stats")
            st.metric("Current", f"{df_predictions['cost_variance'].iloc[-1]:.1f}%")
            st.metric("Average", f"{df_predictions['cost_variance'].mean():.1f}%")
            st.metric("Max Overrun", f"{df_predictions['cost_variance'].max():.1f}%")
            st.metric("Min (Under)", f"{df_predictions['cost_variance'].min():.1f}%")
            
            under_budget = len(df_predictions[df_predictions['cost_variance'] < 0])
            on_budget = len(df_predictions[(df_predictions['cost_variance'] >= 0) & (df_predictions['cost_variance'] < 5)])
            overrun = len(df_predictions[df_predictions['cost_variance'] >= 5])
            
            st.markdown("### 📊 Budget Status")
            st.metric("✅ Under Budget", under_budget)
            st.metric("🟡 On Track", on_budget)
            st.metric("🔴 Overrun", overrun)
    
    with tab3:
        st.subheader("Project-Level Trends")
        
        # Project selector
        project_list = sorted(df_predictions['project_id'].unique())
        selected_project = st.selectbox("Select Project", project_list)
        
        if selected_project:
            # Get trend data for selected project
            trend_data = db.get_project_risk_trend(selected_project, days=30)
            
            if trend_data:
                df_trend = pd.DataFrame(trend_data)
                df_trend['timestamp'] = pd.to_datetime(df_trend['timestamp'])
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Risk score trend
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df_trend['timestamp'],
                        y=df_trend['risk_score'],
                        mode='lines+markers',
                        name='Risk Score',
                        line=dict(color='red', width=2)
                    ))
                    fig.update_layout(
                        title=f"Risk Trend: {selected_project}",
                        xaxis_title="Date",
                        yaxis_title="Risk Score",
                        height=350
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Cost variance trend
                    fig2 = go.Figure()
                    fig2.add_trace(go.Scatter(
                        x=df_trend['timestamp'],
                        y=df_trend['cost_variance'],
                        mode='lines+markers',
                        name='Cost Variance',
                        line=dict(color='blue', width=2)
                    ))
                    fig2.update_layout(
                        title=f"Cost Trend: {selected_project}",
                        xaxis_title="Date",
                        yaxis_title="Cost Variance (%)",
                        height=350
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                
                # Stats
                st.markdown("### 📊 Project Statistics")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Predictions", len(df_trend))
                with col2:
                    st.metric("Avg Risk", f"{df_trend['risk_score'].mean():.1f}")
                with col3:
                    st.metric("Risk Trend", 
                             "📈" if df_trend['risk_score'].iloc[-1] > df_trend['risk_score'].iloc[0] else "📉")
                with col4:
                    st.metric("Latest Risk", f"{df_trend['risk_score'].iloc[-1]}")
            else:
                st.info(f"No historical data available for {selected_project}")
    
    with tab4:
        st.subheader("🔔 Activity Log - Last 24 Hours")
        
        activity_log = db.get_activity_log(hours=24, limit=100)
        
        if activity_log:
            df_activity = pd.DataFrame(activity_log)
            df_activity['timestamp'] = pd.to_datetime(df_activity['timestamp'])
            
            # Color code by severity
            def severity_badge(severity):
                if severity == "HIGH":
                    return "🔴 HIGH"
                elif severity == "MEDIUM":
                    return "🟡 MEDIUM"
                else:
                    return "🟢 LOW"
            
            df_activity['severity_badge'] = df_activity['severity'].apply(severity_badge)
            
            # Display table
            st.dataframe(
                df_activity[['timestamp', 'event_type', 'project_id', 'description', 'severity_badge']].rename(columns={
                    'timestamp': 'Time',
                    'event_type': 'Event',
                    'project_id': 'Project',
                    'description': 'Description',
                    'severity_badge': 'Severity'
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No activity logged yet. Generate some predictions!")
    
    # Recent predictions table
    st.markdown("---")
    st.subheader("📋 Recent Predictions (Last 20)")
    
    recent = df_predictions.head(20)[['timestamp', 'project_id', 'risk_score', 'cost_variance', 'success_probability']]
    recent['timestamp'] = pd.to_datetime(recent['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
    recent['risk_score'] = recent['risk_score'].apply(lambda x: f"{'🔴' if x > 70 else '🟡' if x > 40 else '🟢'} {x}")
    recent['cost_variance'] = recent['cost_variance'].apply(lambda x: f"{x:.1f}%")
    recent['success_probability'] = recent['success_probability'].apply(lambda x: f"{x*100:.1f}%" if pd.notna(x) else "N/A")
    
    st.dataframe(recent, use_container_width=True, hide_index=True)

else:
    st.info("📊 No data yet. Click 'Generate New Prediction' in the sidebar to get started!")

# Footer with auto-refresh
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if auto_refresh:
        st.success("🔄 Auto-refresh enabled - Dashboard updates every 5 seconds")
        time.sleep(5)
        st.rerun()
    else:
        if st.button("🔄 Refresh Dashboard", use_container_width=True):
            st.rerun()

st.caption("📊 Portfolio ML Real-Time Dashboard | 💾 SQLite Persistence | 🟢 All data saved to database")
