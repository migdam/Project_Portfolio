"""Real-Time Portfolio Tracking Dashboard with Live Charts"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time

# Page configuration
st.set_page_config(
    page_title="Portfolio ML - Real-Time Tracking",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .success-metric {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    .warning-metric {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for tracking
if 'start_time' not in st.session_state:
    st.session_state.start_time = datetime.now()
    st.session_state.predictions_count = 0
    st.session_state.accuracy_history = []
    st.session_state.risk_history = []
    st.session_state.cost_history = []

# Header
st.title("📊 Portfolio ML - Real-Time Tracking Dashboard")
st.markdown("### Live monitoring of ML predictions, accuracy metrics, and portfolio health")

# Sidebar controls
with st.sidebar:
    st.header("⚙️ Dashboard Controls")
    
    auto_refresh = st.checkbox("Auto-refresh (every 5s)", value=False)
    
    st.markdown("---")
    st.header("📈 Model Status")
    
    # Model health indicators
    models = {
        "PRM": {"status": "✅", "accuracy": 89, "predictions": np.random.randint(150, 200)},
        "COP": {"status": "✅", "accuracy": 82, "predictions": np.random.randint(150, 200)},
        "SLM": {"status": "✅", "accuracy": 91, "predictions": np.random.randint(150, 200)},
        "PO": {"status": "✅", "accuracy": 87, "predictions": np.random.randint(40, 60)}
    }
    
    for model, info in models.items():
        st.metric(
            f"{info['status']} {model}",
            f"{info['accuracy']}%",
            f"{info['predictions']} predictions"
        )
    
    st.markdown("---")
    st.markdown("**🕐 Uptime**")
    uptime = datetime.now() - st.session_state.start_time
    st.info(f"{uptime.seconds // 3600}h {(uptime.seconds % 3600) // 60}m {uptime.seconds % 60}s")
    
    st.markdown("---")
    if st.button("🔄 Reset Tracking"):
        st.session_state.start_time = datetime.now()
        st.session_state.predictions_count = 0
        st.session_state.accuracy_history = []
        st.session_state.risk_history = []
        st.session_state.cost_history = []
        st.rerun()

# Generate real-time data
def generate_realtime_data():
    """Simulate real-time data updates"""
    current_time = datetime.now()
    
    # Simulate prediction accuracy over time
    base_accuracy = 85
    accuracy = base_accuracy + np.random.normal(0, 2)
    st.session_state.accuracy_history.append({
        'timestamp': current_time,
        'accuracy': accuracy
    })
    
    # Simulate risk scores
    risk_score = np.random.randint(20, 90)
    st.session_state.risk_history.append({
        'timestamp': current_time,
        'risk_score': risk_score,
        'project': f"PROJ-{np.random.randint(1, 50):03d}"
    })
    
    # Simulate cost predictions
    cost_variance = np.random.uniform(-5, 25)
    st.session_state.cost_history.append({
        'timestamp': current_time,
        'variance': cost_variance,
        'project': f"PROJ-{np.random.randint(1, 50):03d}"
    })
    
    st.session_state.predictions_count += 1
    
    # Keep last 100 records
    if len(st.session_state.accuracy_history) > 100:
        st.session_state.accuracy_history = st.session_state.accuracy_history[-100:]
    if len(st.session_state.risk_history) > 100:
        st.session_state.risk_history = st.session_state.risk_history[-100:]
    if len(st.session_state.cost_history) > 100:
        st.session_state.cost_history = st.session_state.cost_history[-100:]

# Generate new data point
generate_realtime_data()

# Top metrics row
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Predictions", f"{st.session_state.predictions_count:,}", "+1")

with col2:
    if st.session_state.accuracy_history:
        current_acc = st.session_state.accuracy_history[-1]['accuracy']
        st.metric("Current Accuracy", f"{current_acc:.1f}%", f"+{current_acc - 85:.1f}%")
    else:
        st.metric("Current Accuracy", "N/A")

with col3:
    high_risk_count = sum(1 for r in st.session_state.risk_history[-10:] if r['risk_score'] > 70)
    st.metric("High Risk Alerts", high_risk_count, f"{high_risk_count}/10")

with col4:
    if st.session_state.cost_history:
        avg_variance = np.mean([c['variance'] for c in st.session_state.cost_history[-10:]])
        st.metric("Avg Cost Variance", f"{avg_variance:.1f}%", f"{'↓' if avg_variance < 10 else '↑'}")
    else:
        st.metric("Avg Cost Variance", "N/A")

with col5:
    processing_speed = st.session_state.predictions_count / max(1, (datetime.now() - st.session_state.start_time).seconds)
    st.metric("Processing Speed", f"{processing_speed:.2f}/sec", "Real-time")

st.markdown("---")

# Create tabs for different views
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Live Accuracy Tracking",
    "🎯 Risk Score Timeline",
    "💰 Cost Variance Monitor",
    "📊 Portfolio Health"
])

with tab1:
    st.subheader("Model Accuracy Over Time")
    
    if len(st.session_state.accuracy_history) > 1:
        df_accuracy = pd.DataFrame(st.session_state.accuracy_history)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Line chart with confidence band
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df_accuracy['timestamp'],
                y=df_accuracy['accuracy'],
                mode='lines+markers',
                name='Accuracy',
                line=dict(color='#667eea', width=3),
                marker=dict(size=6)
            ))
            
            # Add target line
            fig.add_hline(y=85, line_dash="dash", line_color="green", 
                         annotation_text="Target: 85%")
            
            # Add threshold line
            fig.add_hline(y=80, line_dash="dash", line_color="orange",
                         annotation_text="Warning: 80%")
            
            fig.update_layout(
                title="Real-Time Prediction Accuracy",
                xaxis_title="Time",
                yaxis_title="Accuracy (%)",
                height=400,
                hovermode='x unified',
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 Statistics")
            st.metric("Current", f"{df_accuracy['accuracy'].iloc[-1]:.1f}%")
            st.metric("Average", f"{df_accuracy['accuracy'].mean():.1f}%")
            st.metric("Best", f"{df_accuracy['accuracy'].max():.1f}%")
            st.metric("Worst", f"{df_accuracy['accuracy'].min():.1f}%")
            st.metric("Std Dev", f"{df_accuracy['accuracy'].std():.2f}%")
    else:
        st.info("📊 Collecting accuracy data... Refresh in a few seconds.")

with tab2:
    st.subheader("Risk Score Timeline - Last 50 Predictions")
    
    if len(st.session_state.risk_history) > 1:
        df_risk = pd.DataFrame(st.session_state.risk_history[-50:])
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Scatter plot with color coding
            fig = px.scatter(
                df_risk,
                x='timestamp',
                y='risk_score',
                color='risk_score',
                color_continuous_scale=['green', 'yellow', 'orange', 'red'],
                size=[10]*len(df_risk),
                hover_data=['project'],
                title="Project Risk Scores Over Time"
            )
            
            # Add risk zones
            fig.add_hrect(y0=0, y1=30, fillcolor="green", opacity=0.1, line_width=0)
            fig.add_hrect(y0=30, y1=60, fillcolor="yellow", opacity=0.1, line_width=0)
            fig.add_hrect(y0=60, y1=80, fillcolor="orange", opacity=0.1, line_width=0)
            fig.add_hrect(y0=80, y1=100, fillcolor="red", opacity=0.1, line_width=0)
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 🎯 Risk Distribution")
            low = sum(1 for r in df_risk['risk_score'] if r < 30)
            medium = sum(1 for r in df_risk['risk_score'] if 30 <= r < 60)
            high = sum(1 for r in df_risk['risk_score'] if 60 <= r < 80)
            critical = sum(1 for r in df_risk['risk_score'] if r >= 80)
            
            st.metric("🟢 Low (0-30)", low)
            st.metric("🟡 Medium (30-60)", medium)
            st.metric("🟠 High (60-80)", high)
            st.metric("🔴 Critical (80+)", critical)
    else:
        st.info("🎯 Collecting risk data... Refresh in a few seconds.")

with tab3:
    st.subheader("Cost Variance Monitor - Real-Time Predictions")
    
    if len(st.session_state.cost_history) > 1:
        df_cost = pd.DataFrame(st.session_state.cost_history[-50:])
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Bar chart with color coding
            colors = ['green' if v < 5 else 'yellow' if v < 15 else 'red' 
                     for v in df_cost['variance']]
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=df_cost.index,
                y=df_cost['variance'],
                marker_color=colors,
                text=df_cost['variance'].round(1),
                textposition='outside',
                hovertext=df_cost['project']
            ))
            
            fig.add_hline(y=0, line_color="gray", line_width=1)
            fig.add_hline(y=15, line_dash="dash", line_color="red",
                         annotation_text="Critical: 15%")
            
            fig.update_layout(
                title="Cost Variance Predictions",
                xaxis_title="Prediction #",
                yaxis_title="Variance (%)",
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 💰 Variance Stats")
            st.metric("Current", f"{df_cost['variance'].iloc[-1]:.1f}%")
            st.metric("Average", f"{df_cost['variance'].mean():.1f}%")
            st.metric("Max Overrun", f"{df_cost['variance'].max():.1f}%")
            
            under_budget = sum(1 for v in df_cost['variance'] if v < 0)
            on_budget = sum(1 for v in df_cost['variance'] if 0 <= v < 5)
            overrun = sum(1 for v in df_cost['variance'] if v >= 5)
            
            st.markdown("### 📊 Budget Status")
            st.metric("✅ Under Budget", under_budget)
            st.metric("🟡 On Track", on_budget)
            st.metric("🔴 Overrun", overrun)
    else:
        st.info("💰 Collecting cost data... Refresh in a few seconds.")

with tab4:
    st.subheader("Overall Portfolio Health Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Portfolio health gauge
        if st.session_state.risk_history:
            avg_risk = np.mean([r['risk_score'] for r in st.session_state.risk_history[-20:]])
            health_score = 100 - avg_risk
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=health_score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Portfolio Health Score"},
                delta={'reference': 70, 'increasing': {'color': "green"}},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 40], 'color': "lightgray"},
                        {'range': [40, 70], 'color': "gray"},
                        {'range': [70, 100], 'color': "lightgreen"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Success rate prediction
        success_rate = 85 + np.random.normal(0, 3)
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=success_rate,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Predicted Success Rate"},
            delta={'reference': 68, 'increasing': {'color': "green"}},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "green"},
                'steps': [
                    {'range': [0, 50], 'color': "lightcoral"},
                    {'range': [50, 75], 'color': "lightyellow"},
                    {'range': [75, 100], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "gold", 'width': 4},
                    'thickness': 0.75,
                    'value': 85
                }
            }
        ))
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # Portfolio summary metrics
    st.markdown("### 📈 Portfolio Summary (Last Hour)")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Projects Analyzed",
            len(set([r['project'] for r in st.session_state.risk_history])),
            "Real-time"
        )
    
    with col2:
        if st.session_state.risk_history:
            high_risk = sum(1 for r in st.session_state.risk_history if r['risk_score'] > 70)
            st.metric("High Risk Projects", high_risk, "Needs attention")
        else:
            st.metric("High Risk Projects", 0)
    
    with col3:
        if st.session_state.cost_history:
            overruns = sum(1 for c in st.session_state.cost_history if c['variance'] > 15)
            st.metric("Cost Overrun Alerts", overruns, "Monitor closely")
        else:
            st.metric("Cost Overrun Alerts", 0)
    
    with col4:
        predictions_per_min = st.session_state.predictions_count / max(1, (datetime.now() - st.session_state.start_time).seconds / 60)
        st.metric("Predictions/min", f"{predictions_per_min:.1f}", "Processing rate")

# Real-time activity log
st.markdown("---")
st.subheader("🔔 Recent Activity Feed")

if st.session_state.risk_history:
    recent_activities = []
    
    # Last 10 activities
    for i, (risk, cost) in enumerate(zip(
        st.session_state.risk_history[-10:][::-1],
        st.session_state.cost_history[-10:][::-1]
    )):
        activity_time = risk['timestamp'].strftime("%H:%M:%S")
        risk_level = "🔴" if risk['risk_score'] > 70 else "🟡" if risk['risk_score'] > 40 else "🟢"
        cost_level = "🔴" if cost['variance'] > 15 else "🟡" if cost['variance'] > 5 else "🟢"
        
        recent_activities.append({
            "Time": activity_time,
            "Project": risk['project'],
            "Risk": f"{risk_level} {risk['risk_score']:.0f}",
            "Cost Variance": f"{cost_level} {cost['variance']:.1f}%",
            "Status": "✅ Analyzed"
        })
    
    df_activities = pd.DataFrame(recent_activities)
    st.dataframe(df_activities, use_container_width=True, hide_index=True)
else:
    st.info("📋 Activity feed will appear here as predictions are made...")

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

st.markdown("---")
st.caption("📊 Portfolio ML Real-Time Dashboard | Powered by Streamlit & Plotly | 🟢 All systems operational")
