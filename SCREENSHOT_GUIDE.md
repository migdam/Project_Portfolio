# Screenshot Capture Guide for UI

This guide helps you capture screenshots of the AI Portfolio Agent UI for documentation.

## Quick Capture Instructions

### 1. Launch the UI

```bash
./launch_ui.sh
```

Wait for the UI to open at `http://localhost:8501`

### 2. Capture Screenshots

**On macOS:**
- Full screen: `Cmd + Shift + 3`
- Selected area: `Cmd + Shift + 4` (recommended)
- Window: `Cmd + Shift + 4`, then press `Space`, click window

### 3. Screenshots Needed

#### Screenshot 1: Orchestration Dashboard (Main View)
**Filename:** `ui_orchestration_dashboard.png`
**Location:** `assets/screenshots/`

**Steps:**
1. Click "Load Sample Ideas" and "Load Sample Projects" in sidebar
2. Go to "🎯 Orchestration Dashboard" tab
3. Click "🚀 Run Full Orchestration"
4. Wait for results to appear
5. Capture full page showing:
   - Key metrics cards at top
   - Master recommendations section
   - Idea evaluations (expanded)
   - Project health monitoring table

**Screenshot should show:**
- All 4 metric cards (Ideas Evaluated, Projects Monitored, Critical Items, Total Recommendations)
- At least 2 master recommendations with color coding
- Sequencing optimization section with critical path
- Location assignments with bar chart

---

#### Screenshot 2: Idea Evaluation Form
**Filename:** `ui_idea_evaluation.png`
**Location:** `assets/screenshots/`

**Steps:**
1. Go to "📝 Idea Evaluation" tab
2. Fill out the form with sample data:
   - Title: "AI Customer Service Chatbot"
   - Cost: $500,000
   - Duration: 6 months
   - Strategic Alignment: 85
   - ROI: 200%
3. Click "🤖 Evaluate with Agent"
4. Capture showing:
   - Filled form on left
   - Agent decision box with confidence score
   - Ideas list in right panel

**Screenshot should show:**
- Complete form with all fields filled
- Agent decision (e.g., "FAST_TRACK" with 95% confidence)
- Reasoning text below decision

---

#### Screenshot 3: Project Monitoring
**Filename:** `ui_project_monitoring.png`
**Location:** `assets/screenshots/`

**Steps:**
1. Load sample projects from sidebar
2. Go to "📊 Project Monitoring" tab
3. Select "PROJ-101" from dropdown
4. Click "🤖 Monitor with Agent"
5. Capture showing:
   - Projects table at top
   - Selected project dropdown
   - Health status display (colored box)
   - Agent recommended actions

**Screenshot should show:**
- Active projects table with all columns
- Health status badge (green/yellow/red)
- At least one recommended action

---

#### Screenshot 4: Configuration Panel
**Filename:** `ui_configuration.png`
**Location:** `assets/screenshots/`

**Steps:**
1. Go to "⚙️ Configuration" tab
2. Capture showing:
   - Location resources section (US/EU/APAC)
   - All resource input fields
   - Resource constraints section at bottom

**Screenshot should show:**
- All 3 location columns (US, EU, APAC)
- Engineering/Design/PM fields for each
- Global constraints at bottom

---

#### Screenshot 5: Sidebar with Sample Data Loaded
**Filename:** `ui_sidebar.png`
**Location:** `assets/screenshots/`

**Steps:**
1. Ensure agent is initialized (green status)
2. Load sample ideas and projects
3. Capture showing:
   - Configuration section at top
   - Agent status indicator (green)
   - Mode display (LLM-powered or Rule-based)
   - Quick Actions section with loaded data confirmation

**Screenshot should show:**
- "🟢 Agent: Active" status
- Success messages after loading data
- All quick action buttons

---

#### Screenshot 6: Master Recommendations (Close-up)
**Filename:** `ui_recommendations.png`
**Location:** `assets/screenshots/`

**Steps:**
1. Run full orchestration
2. Scroll to Master Recommendations section
3. Capture showing only the recommendations cards
4. Should show 3-4 recommendations with different priority levels

**Screenshot should show:**
- Multiple recommendation cards
- Different colors (red for HIGH, orange for CRITICAL, yellow for MEDIUM)
- Full recommendation text

---

## Screenshot Specifications

**Format:** PNG (preferred) or JPG
**Size:** Max width 1200px (Streamlit default width)
**Quality:** High (for readability of text)
**Naming:** Use descriptive names with `ui_` prefix

## Editing Screenshots (Optional)

If you want to highlight specific areas:

1. Open screenshot in Preview (macOS)
2. Use markup tools to add:
   - Arrows pointing to key features
   - Red boxes around important elements
   - Text annotations

**Don't overdo it** - clean screenshots are often better.

## Saving Screenshots

```bash
# Save all screenshots to the correct location
mv ~/Desktop/ui_*.png /Users/michalmigda/Scripts/Project_Portfolio/assets/screenshots/

# Or create them directly there by using this location in the save dialog
```

## After Capturing

Once you have the screenshots, the README will automatically reference them. The paths are already set up in the README:

- `assets/screenshots/ui_orchestration_dashboard.png`
- `assets/screenshots/ui_idea_evaluation.png`
- `assets/screenshots/ui_project_monitoring.png`
- `assets/screenshots/ui_configuration.png`
- `assets/screenshots/ui_sidebar.png`
- `assets/screenshots/ui_recommendations.png`

## Troubleshooting

**Issue: UI looks cramped**
- Zoom out in browser (Cmd + -)
- Or use full-screen mode

**Issue: Screenshots too large**
- Use Preview to resize: Tools → Adjust Size → Width: 1200px

**Issue: Text blurry**
- Use PNG format
- Don't resize too much
- Take screenshot at 2x resolution (Retina display)

## Quick Workflow

```bash
# 1. Launch UI
./launch_ui.sh

# 2. In browser:
#    - Initialize agent
#    - Load sample data
#    - Navigate through tabs
#    - Capture screenshots (Cmd+Shift+4)

# 3. Save to assets/screenshots/
#    - Use naming convention: ui_*.png

# 4. Commit
git add assets/screenshots/ui_*.png
git commit -m "docs: Add UI screenshots"
git push
```

---

**Estimated Time:** 10-15 minutes to capture all screenshots
