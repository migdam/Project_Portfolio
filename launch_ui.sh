#!/bin/bash
# Launch AI Portfolio Agent Orchestrator UI

echo "🤖 Launching AI Portfolio Agent Orchestrator UI..."
echo ""

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit not found. Installing dependencies..."
    pip install -r requirements_ui.txt
fi

# Launch Streamlit app
echo "🚀 Starting Streamlit server..."
echo ""
echo "📱 UI will open at: http://localhost:8501"
echo ""

streamlit run ui_agent_orchestrator.py
