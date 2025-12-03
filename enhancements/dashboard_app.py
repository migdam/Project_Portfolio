"""Streamlit dashboard for model insights."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from models import ProjectRiskModel, CostOverrunPredictor, SuccessLikelihoodModel
from utils.config import load_config
from enhancements.visualizations import PortfolioVisualizer

st.set_page_config(page_title="Portfolio ML Dashboard", layout="wide")

@st.cache_resource
def load_models():
    """Load all models."""
    config = load_config()
    models = {}
    for name in ['prm', 'cop', 'slm']:
        try:
            model_class = {'prm': ProjectRiskModel, 'cop': CostOverrunPredictor, 'slm': SuccessLikelihoodModel}[name]
            model = model_class(config)
            model.load_model("models/artifacts")
            models[name] = model
        except:
            models[name] = None
    return models

def main():
    st.title("🎯 Portfolio ML Dashboard")
    st.markdown("AI-Powered Project & Portfolio Management Analytics")
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a page", ["Overview", "Predictions", "Analysis", "Monitoring"])
    
    models = load_models()
    
    if page == "Overview":
        st.header("Model Status")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Risk Model (PRM)", "✅ Loaded" if models['prm'] else "❌ Not Loaded")
        with col2:
            st.metric("Cost Model (COP)", "✅ Loaded" if models['cop'] else "❌ Not Loaded")
        with col3:
            st.metric("Success Model (SLM)", "✅ Loaded" if models['slm'] else "❌ Not Loaded")
    
    elif page == "Predictions":
        st.header("Make Predictions")
        
        uploaded_file = st.file_uploader("Upload project data (CSV)", type=['csv'])
        
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.write(f"Loaded {len(df)} projects")
            st.dataframe(df.head())
            
            if st.button("Run Predictions"):
                with st.spinner("Running predictions..."):
                    if models['prm']:
                        predictions, confidences = models['prm'].predict_with_confidence(df)
                        st.success(f"Risk predictions complete!")
                        st.bar_chart(pd.Series(predictions).value_counts())
    
    elif page == "Analysis":
        st.header("Portfolio Analysis")
        visualizer = PortfolioVisualizer()
        st.info("Upload data to generate visualizations")
    
    elif page == "Monitoring":
        st.header("Model Monitoring")
        st.info("Model health monitoring coming soon")

if __name__ == "__main__":
    main()
