# AI Portfolio Agent Orchestrator UI

**Interactive Web Interface for LangGraph-Powered Portfolio Intelligence**

![UI Version](https://img.shields.io/badge/UI-v1.0.0-blue)
![Framework](https://img.shields.io/badge/Framework-Streamlit-red)
![Status](https://img.shields.io/badge/Status-Production%20Ready-green)

---

## Overview

The AI Portfolio Agent Orchestrator UI provides an interactive, real-time dashboard for managing your entire portfolio through the LangGraph-powered autonomous agent.

**Key Features:**
- 🤖 **Real-time Agent Orchestration** - Watch the AI agent evaluate, monitor, and optimize
- 📊 **Interactive Visualizations** - Charts, metrics, and color-coded insights
- 💡 **Master Recommendations Feed** - Agent-prioritized actions for executives
- 🎯 **Multi-Tab Interface** - Organized workflow for different tasks
- 🔄 **Live Updates** - Immediate feedback on agent decisions
- 🎨 **Modern Design** - Clean, professional interface with custom styling

---

## Quick Start

### 1. Install Dependencies

```bash
# Using pip
pip install -r requirements_ui.txt

# Or using conda
conda activate project_portfolio
pip install streamlit plotly pandas
```

### 2. Launch the UI

**Option A: Using the launch script (recommended)**
```bash
./launch_ui.sh
```

**Option B: Direct launch**
```bash
streamlit run ui_agent_orchestrator.py
```

The UI will automatically open in your browser at `http://localhost:8501`

### 3. Initialize the Agent

1. Click **"🚀 Initialize Agent"** in the sidebar
2. Optionally enter an OpenAI API key (or leave blank for rule-based mode)
3. Wait for "✅ Agent ready!" confirmation

### 4. Load Sample Data

Click the quick action buttons in the sidebar:
- **📝 Load Sample Ideas** - Loads 2 project ideas for evaluation
- **📊 Load Sample Projects** - Loads 3 active projects for monitoring

### 5. Run Orchestration

Navigate to the **🎯 Orchestration Dashboard** tab and click **"🚀 Run Full Orchestration"**

---

## UI Features

### Main Tabs

#### 🎯 Tab 1: Orchestration Dashboard

**Purpose:** Run complete portfolio orchestration and view unified results

**Features:**
- **Run Full Orchestration Button** - Executes agent across all features
- **Key Metrics Cards** - Ideas evaluated, projects monitored, critical items, recommendations
- **Master Recommendations Feed** - Prioritized actions (HIGH, CRITICAL, MEDIUM)
- **Idea Evaluation Results** - Expandable cards showing routing decisions and confidence
- **Project Health Monitoring** - Color-coded health status table (🟢 HEALTHY, 🟡 AT_RISK, 🔴 CRITICAL)
- **Sequencing Optimization** - Critical path visualization and timeline insights
- **Location Assignments** - Bar chart showing project distribution across US/EU/APAC

**Workflow:**
1. Ensure data is loaded (ideas and projects)
2. Click "Run Full Orchestration"
3. Watch agent thinking spinner
4. Review master recommendations first
5. Drill down into specific areas as needed

**Example Output:**
```
📊 Key Metrics
- Ideas Evaluated: 2
- Projects Monitored: 3
- Critical Items: 1
- Total Recommendations: 4

💡 Master Recommendations
🔴 [HIGH] FAST_TRACK_APPROVAL
  Expedite approval and resource allocation for IDEA-001

⚠️ [CRITICAL] INTERVENTION_REQUIRED
  Immediate executive attention needed for PROJ-103

🟡 [MEDIUM] PORTFOLIO_HEALTH
  Portfolio contains 3 active projects with 2 pending evaluations
```

---

#### 📝 Tab 2: Idea Evaluation

**Purpose:** Submit and evaluate individual project ideas with agent

**Features:**
- **New Idea Form** - Input project details
  - Project ID (auto-generated)
  - Title and description
  - Cost and duration
  - Strategic alignment (0-100 slider)
  - Expected ROI
  - Risk level (LOW/MEDIUM/HIGH/CRITICAL)
  - Complexity (LOW/MEDIUM/HIGH/VERY_HIGH)
- **Agent Evaluation Button** - Submit to agent for instant routing decision
- **Real-time Results** - Agent decision with confidence score and reasoning
- **Ideas List** - View all submitted ideas in sidebar panel

**Workflow:**
1. Fill out idea form (all fields required)
2. Click "🤖 Evaluate with Agent"
3. Watch agent thinking spinner
4. Review agent decision and reasoning
5. Idea is automatically added to portfolio

**Example Result:**
```
🤖 Agent Decision: FAST_TRACK
(Confidence: 95%)

Reasoning: High priority score (85/100) - expedite for 
immediate portfolio inclusion
```

**Agent Actions:**
- **FAST_TRACK** - High-priority, approve immediately
- **STANDARD_REVIEW** - Medium priority, next planning cycle
- **CONDITIONAL_APPROVAL** - Lower priority, approve if resources available
- **HUMAN_REVIEW_REQUIRED** - High risk/uncertainty, escalate to executive
- **REJECT_WITH_FEEDBACK** - Does not meet criteria, provide feedback

---

#### 📊 Tab 3: Project Monitoring

**Purpose:** Monitor active project health and benefit realization

**Features:**
- **Active Projects Table** - Overview of all projects
  - Project ID
  - Duration
  - Priority score
  - Strategic value
  - NPV
- **Project Selector** - Choose project to analyze
- **Agent Monitoring Button** - Run benefit health check
- **Health Status Display** - Color-coded status (HEALTHY/AT_RISK/CRITICAL)
- **Agent Recommended Actions** - Interventions based on health

**Workflow:**
1. Load sample projects (or add your own)
2. Select a project from dropdown
3. Click "🤖 Monitor with Agent"
4. Review health status and recommended actions

**Health Status Meanings:**
- **🟢 HEALTHY (≥90% realization)** - On track, capture best practices
- **🟡 AT_RISK (70-89% realization)** - Monitor closely, increase frequency
- **🔴 CRITICAL (<70% realization)** - Immediate intervention required

**Example Output:**
```
🔴 Health Status: CRITICAL

Agent Recommended Actions:
• IMMEDIATE_INTERVENTION: Low realization rate (55%) - 
  root cause analysis required
```

---

#### ⚙️ Tab 4: Configuration

**Purpose:** Configure resource capacity and constraints

**Features:**
- **Location Resources** - Set capacity for US/EU/APAC
  - Engineering headcount
  - Design headcount
  - PM headcount
- **Resource Constraints** - Global portfolio limits
  - Max Engineering
  - Max Design
  - Max PM

**Default Values:**
```
US:     Engineering 50, Design 15, PM 10
EU:     Engineering 40, Design 12, PM 8
APAC:   Engineering 30, Design 10, PM 6

Global: Engineering 100, Design 30, PM 20
```

**Note:** Configuration changes take effect on next orchestration run.

---

### Sidebar Features

#### ⚙️ Configuration Panel

**API Key Input:**
- Optional OpenAI API key for LLM-powered reasoning
- Leave blank to use rule-based fallback (no API costs)
- Secure password input (hidden)

**Initialize Agent Button:**
- Creates orchestrator instance
- Validates API key (if provided)
- Shows success/error status

**Agent Status Indicator:**
- 🟢 Active - Agent ready to orchestrate
- 🟡 Not initialized - Need to initialize first
- Mode display: LLM-powered or Rule-based

#### 🎯 Quick Actions

**Load Sample Ideas:**
- Loads 2 pre-configured project ideas
- AI Customer Service Chatbot ($500K, 6 months)
- Legacy System Migration ($2M, 18 months)

**Load Sample Projects:**
- Loads 3 active projects with dependencies
- PROJ-101: Foundation project (no dependencies)
- PROJ-102: Depends on PROJ-101
- PROJ-103: Independent project

---

## Visual Guide

### Color Coding

**Recommendation Priority:**
- 🔴 **RED** - HIGH priority (action needed soon)
- ⚠️ **ORANGE** - CRITICAL priority (urgent attention required)
- 🟡 **YELLOW** - MEDIUM priority (informational)

**Health Status:**
- 🟢 **GREEN** - Healthy (≥90% realization)
- 🟡 **YELLOW** - At Risk (70-89% realization)
- 🔴 **RED** - Critical (<70% realization)

**Agent Status:**
- 🟢 **GREEN** - Active and ready
- 🟡 **YELLOW** - Not initialized

### Agent Thinking Indicator

When the agent is processing:
```
🤖 Agent is thinking...
```

This appears as:
- Spinner animation during orchestration
- Blue background box with italic text
- Typically completes in 1-3 seconds

---

## Use Cases

### Use Case 1: Weekly Portfolio Review

**Scenario:** Executive wants a weekly portfolio health check

**Steps:**
1. Launch UI: `./launch_ui.sh`
2. Initialize agent (sidebar)
3. Load current active projects
4. Go to **Orchestration Dashboard**
5. Click **Run Full Orchestration**
6. Review **Master Recommendations**
7. Export/screenshot key metrics for leadership meeting

**Time:** ~2 minutes

---

### Use Case 2: Rapid Idea Triage

**Scenario:** 10 new project ideas submitted this week

**Steps:**
1. Launch UI
2. Initialize agent
3. Go to **Idea Evaluation** tab
4. For each idea:
   - Fill out form with idea details
   - Click **Evaluate with Agent**
   - Note agent decision and confidence
   - Move to next idea
5. Review all ideas in sidebar
6. Follow up on FAST_TRACK items immediately

**Time:** ~30 seconds per idea (5 minutes for 10 ideas)

---

### Use Case 3: Project Health Monitoring

**Scenario:** Mid-quarter check-in on 20 active projects

**Steps:**
1. Launch UI
2. Initialize agent
3. Load all active projects
4. Go to **Project Monitoring** tab
5. For each project:
   - Select from dropdown
   - Click **Monitor with Agent**
   - Note health status
   - Review recommended actions
6. Escalate CRITICAL projects to PMO

**Time:** ~20 seconds per project (7 minutes for 20 projects)

---

### Use Case 4: Portfolio Planning Session

**Scenario:** Quarterly portfolio planning - optimize mix of projects

**Steps:**
1. Launch UI
2. Initialize agent with LLM mode (enter API key)
3. Load all proposed ideas (from intake)
4. Load all active projects (from PMO tool)
5. Configure location resources (Tab 4)
6. Run **Full Orchestration** (Tab 1)
7. Review:
   - Which ideas to approve (fast-track vs standard)
   - Project health issues requiring intervention
   - Sequencing recommendations (critical path)
   - Location assignments (optimal sites)
8. Use agent recommendations as input to planning discussion

**Time:** ~10 minutes

---

## Advanced Features

### Agent Modes

**Rule-Based Mode (No API Key):**
- Uses predefined business rules
- Instant responses (<1 second)
- No API costs
- Consistent, repeatable decisions
- Good for: Standard evaluations, high-volume processing

**LLM-Powered Mode (With API Key):**
- Uses OpenAI GPT-4 for deep reasoning
- Nuanced edge case handling
- Explains complex tradeoffs
- ~2-5 seconds per decision
- Small API costs (~$0.01 per orchestration)
- Good for: Complex decisions, strategic planning

### Custom Styling

The UI includes custom CSS for professional appearance:
- Color-coded recommendation cards
- Responsive layout (works on tablets)
- Clean typography
- Intuitive spacing
- Hover effects on interactive elements

### Data Persistence

**Session State:**
- Ideas and projects persist during session
- Orchestration results cached
- Agent configuration saved
- Browser refresh clears state

**To Persist Data:**
- Export results to JSON (future feature)
- Take screenshots of key metrics
- Copy recommendations to external tool

---

## Troubleshooting

### Issue: Agent Not Initializing

**Symptoms:**
- "Agent: Not initialized" stays yellow
- Error message on initialization

**Solutions:**
1. Check that all dependencies are installed: `pip list | grep streamlit`
2. Verify Python path: `which python`
3. Try without API key (rule-based mode)
4. Check console for error messages
5. Restart Streamlit server

---

### Issue: Data Not Loading

**Symptoms:**
- "Load Sample Ideas" button does nothing
- Projects table is empty

**Solutions:**
1. Check browser console (F12) for JavaScript errors
2. Refresh the page
3. Clear browser cache
4. Restart Streamlit server
5. Check file permissions on UI script

---

### Issue: Orchestration Hangs

**Symptoms:**
- "Agent is thinking..." spinner runs forever
- No results displayed

**Solutions:**
1. Check terminal for Python errors
2. Verify all required modules are imported correctly
3. Try with minimal data (1 idea, 1 project)
4. Check API key (if using LLM mode)
5. Restart in rule-based mode

---

### Issue: Visualizations Not Rendering

**Symptoms:**
- Charts/graphs don't appear
- Blank spaces where charts should be

**Solutions:**
1. Ensure Plotly is installed: `pip install plotly`
2. Check browser compatibility (use Chrome/Firefox/Safari)
3. Disable ad blockers
4. Clear browser cache
5. Try different browser

---

## Technical Details

### Architecture

```
ui_agent_orchestrator.py (Streamlit App)
         ↓
integrated_agent_orchestrator.py (Orchestrator)
         ↓
    ┌────┴────┐
    ↓         ↓
langgraph_agent.py  Feature Modules
    ↓               (demand, benefit, etc.)
ML Models (PRM/COP/SLM)
```

### Dependencies

**Required:**
- `streamlit>=1.28.0` - UI framework
- `pandas>=2.0.0` - Data manipulation
- `plotly>=5.17.0` - Interactive charts

**Optional (for LLM mode):**
- `openai>=1.3.0` - GPT-4 integration
- `langchain>=0.1.0` - LLM orchestration
- `langgraph>=0.0.20` - Agent graph framework

### Performance

**Metrics:**
- **Initialization:** <1 second
- **Idea Evaluation:** <1 second (rule-based), 2-3 seconds (LLM)
- **Full Orchestration:** 1-2 seconds (rule-based), 5-10 seconds (LLM)
- **Page Load:** <2 seconds
- **Memory Usage:** ~100-200 MB

**Scalability:**
- Tested with: 50 ideas, 50 projects
- Max recommended: 100 ideas, 100 projects per session
- For larger portfolios: Use batch processing (future feature)

---

## Customization

### Adding Custom Metrics

Edit `ui_agent_orchestrator.py`:

```python
# Add new metric card in Tab 1
with col5:
    st.metric(
        "Custom Metric",
        your_calculated_value,
        help="Your custom metric description"
    )
```

### Changing Color Scheme

Edit CSS section in `ui_agent_orchestrator.py`:

```python
st.markdown("""
<style>
    .main-header {
        color: #YOUR_COLOR;  # Change header color
    }
    .recommendation-high {
        background-color: #YOUR_BG;  # Change card background
        border-left: 4px solid #YOUR_BORDER;
    }
</style>
""", unsafe_allow_html=True)
```

### Adding New Tabs

```python
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 Orchestration Dashboard",
    "📝 Idea Evaluation",
    "📊 Project Monitoring",
    "⚙️ Configuration",
    "📈 Your New Tab"  # Add here
])

with tab5:
    st.header("Your New Feature")
    # Add your content
```

---

## Deployment

### Local Development

```bash
./launch_ui.sh
```

Access at: `http://localhost:8501`

### Production Deployment

**Option 1: Streamlit Cloud (Free)**

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repository
4. Select `ui_agent_orchestrator.py` as main file
5. Deploy

**Option 2: Docker**

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements_ui.txt .
RUN pip install -r requirements_ui.txt

COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "ui_agent_orchestrator.py"]
```

Build and run:
```bash
docker build -t portfolio-agent-ui .
docker run -p 8501:8501 portfolio-agent-ui
```

**Option 3: AWS/GCP/Azure**

Follow platform-specific Streamlit deployment guides.

---

## Future Enhancements

**Planned Features:**
- [ ] Export results to PDF/Excel
- [ ] Email notifications for critical recommendations
- [ ] Historical trend charts
- [ ] Multi-user authentication
- [ ] Role-based access control
- [ ] Real-time collaboration
- [ ] Integration with Jira/Confluence
- [ ] Mobile app version
- [ ] Dark mode toggle
- [ ] Custom dashboard templates

---

## Support

**Documentation:**
- Main README: [README.md](README.md)
- Agent Integration: [DEEP_AGENT_INTEGRATION.md](DEEP_AGENT_INTEGRATION.md)
- UI Documentation: This file

**Issues:**
- Check troubleshooting section above
- Review console/terminal for error messages
- Verify all dependencies installed
- Test with sample data first

**Contact:**
- GitHub Issues: Create issue in repository
- Email: [Your support email]

---

## Version History

**v1.0.0** (December 4, 2024)
- ✅ Initial release
- ✅ Full orchestration dashboard
- ✅ Idea evaluation interface
- ✅ Project monitoring
- ✅ Configuration panel
- ✅ Master recommendations feed
- ✅ Interactive visualizations
- ✅ LLM and rule-based modes

---

## License

MIT License - See [LICENSE](LICENSE) for details

---

**Built with ❤️ using Streamlit and LangGraph**
