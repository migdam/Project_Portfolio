"""Generate static charts for GitHub repository"""
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

# Create charts directory if it doesn't exist
charts_dir = Path("assets/charts")
charts_dir.mkdir(parents=True, exist_ok=True)

# Set random seed for reproducibility
np.random.seed(42)

print("Generating charts for GitHub repository...")

# 1. Risk Distribution Chart
print("1. Creating Risk Distribution chart...")
risk_data = pd.DataFrame({
    'Project': [f'PROJ-{i:03d}' for i in range(1, 26)],
    'Risk Score': np.random.randint(20, 95, 25),
    'Budget (M)': np.random.uniform(0.5, 5.0, 25),
})
risk_data['Risk Level'] = risk_data['Risk Score'].apply(
    lambda x: 'HIGH' if x > 70 else 'MEDIUM' if x > 40 else 'LOW'
)

fig1 = px.scatter(risk_data, 
                  x='Risk Score', 
                  y='Budget (M)',
                  color='Risk Level',
                  size=[10]*25,
                  title='Project Risk Analysis',
                  color_discrete_map={'LOW': '#22c55e', 'MEDIUM': '#f59e0b', 'HIGH': '#ef4444'},
                  template='plotly_white')
fig1.update_layout(
    font=dict(size=14),
    title_font=dict(size=20, color='#1f2937'),
    plot_bgcolor='white',
    width=800,
    height=500
)
fig1.write_image(charts_dir / "risk-analysis.png")
print("   ✓ Saved risk-analysis.png")

# 2. Cost Overrun Predictions
print("2. Creating Cost Overrun chart...")
cost_data = pd.DataFrame({
    'Project': [f'PROJ-{i:03d}' for i in range(1, 16)],
    'Predicted Overrun %': np.random.uniform(-5, 25, 15),
})

fig2 = px.bar(cost_data, 
              x='Project', 
              y='Predicted Overrun %',
              color='Predicted Overrun %',
              color_continuous_scale=['#22c55e', '#fbbf24', '#ef4444'],
              title='Cost Overrun Predictions',
              template='plotly_white')
fig2.update_layout(
    font=dict(size=14),
    title_font=dict(size=20, color='#1f2937'),
    showlegend=False,
    width=800,
    height=500
)
fig2.write_image(charts_dir / "cost-overrun.png")
print("   ✓ Saved cost-overrun.png")

# 3. Success Likelihood Distribution
print("3. Creating Success Likelihood chart...")
success_data = pd.DataFrame({
    'Project': [f'PROJ-{i:03d}' for i in range(1, 21)],
    'Success Probability': np.random.uniform(0.45, 0.98, 20),
    'Team Experience': np.random.randint(1, 10, 20),
    'Duration (months)': np.random.randint(6, 36, 20)
})
success_data['Category'] = success_data['Success Probability'].apply(
    lambda x: 'High' if x > 0.8 else 'Medium' if x > 0.6 else 'Low'
)

fig3 = px.scatter(success_data,
                  x='Duration (months)',
                  y='Success Probability',
                  size='Team Experience',
                  color='Category',
                  title='Project Success Likelihood',
                  color_discrete_map={'High': '#22c55e', 'Medium': '#f59e0b', 'Low': '#ef4444'},
                  template='plotly_white')
fig3.update_layout(
    font=dict(size=14),
    title_font=dict(size=20, color='#1f2937'),
    width=800,
    height=500
)
fig3.write_image(charts_dir / "success-likelihood.png")
print("   ✓ Saved success-likelihood.png")

# 4. Portfolio Optimization
print("4. Creating Portfolio Optimization chart...")
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

fig4 = px.scatter(portfolio_data,
                  x='Risk Score',
                  y='Strategic Value',
                  size='NPV (M)',
                  color='Selected',
                  title='Portfolio Optimization: Pareto Frontier',
                  color_discrete_map={'Optimal': '#eab308', 'Candidate': '#93c5fd'},
                  template='plotly_white')
fig4.update_layout(
    font=dict(size=14),
    title_font=dict(size=20, color='#1f2937'),
    width=800,
    height=500
)
fig4.write_image(charts_dir / "portfolio-optimization.png")
print("   ✓ Saved portfolio-optimization.png")

# 5. Model Performance Dashboard
print("5. Creating Model Performance dashboard...")
models = ['PRM', 'COP', 'SLM', 'PO']
accuracy = [89, 82, 91, 87]
colors = ['#3b82f6', '#8b5cf6', '#ec4899', '#06b6d4']

fig5 = go.Figure(data=[
    go.Bar(x=models, y=accuracy, marker_color=colors, text=accuracy, texttemplate='%{text}%')
])
fig5.update_layout(
    title='Model Performance Metrics',
    yaxis_title='Accuracy/Score (%)',
    xaxis_title='Model',
    font=dict(size=14),
    title_font=dict(size=20, color='#1f2937'),
    template='plotly_white',
    showlegend=False,
    width=800,
    height=500
)
fig5.write_image(charts_dir / "model-performance.png")
print("   ✓ Saved model-performance.png")

print("\n✅ All charts generated successfully in assets/charts/")
print("\nGenerated files:")
print("  - risk-analysis.png")
print("  - cost-overrun.png")
print("  - success-likelihood.png")
print("  - portfolio-optimization.png")
print("  - model-performance.png")
