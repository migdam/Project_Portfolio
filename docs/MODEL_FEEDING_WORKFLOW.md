# Model Feeding Workflow

## 🔄 How Projects Feed the ML Models

### Overview

Projects can be fed to ML models in **two modes**:

1. **Real-Time Mode** (Single Project) - Instant predictions for decision-making
2. **Batch Mode** (Multiple Projects) - Scheduled portfolio-wide analysis

---

## 1️⃣ Real-Time Mode: Single Project Analysis

### When to Use
- Gate review decisions (Go/No-Go)
- Ad-hoc risk assessment requests
- Emergency project health checks
- Executive escalations

### Workflow

```
User Request → API Call → Data Fetch → Model Prediction → Response
```

### Process Flow

```python
# 1. Request comes in for a specific project
project_id = "PROJ-042"

# 2. Fetch project data from systems
project_data = fetch_project_data(project_id)
# Returns: {
#   'project_id': 'PROJ-042',
#   'budget': 5_000_000,
#   'actual_spend': 2_100_000,
#   'start_date': '2024-01-15',
#   'team_size': 12,
#   'milestones_completed': 8,
#   'milestones_total': 20,
#   ... (30+ features)
# }

# 3. Run all 4 models sequentially
results = {
    'risk': PRM.predict(project_data),      # ~50ms
    'cost': COP.predict(project_data),      # ~40ms
    'success': SLM.predict(project_data),   # ~45ms
    'priority': PO.score(project_data)      # ~30ms
}

# 4. Return results with explanations
response = {
    'project_id': 'PROJ-042',
    'timestamp': datetime.now(),
    'predictions': {
        'risk_score': 68,           # HIGH
        'cost_overrun': 12.3,       # 12.3% predicted overrun
        'success_probability': 0.72, # 72% chance of success
        'priority_score': 85        # High priority for portfolio
    },
    'top_risk_factors': [
        'Team turnover rate: 15% (High)',
        'Vendor delays: 2 weeks behind',
        'Scope changes: 8 uncontrolled'
    ],
    'recommendations': [
        'Activate retention bonuses',
        'Escalate vendor issues to C-level',
        'Freeze scope immediately'
    ],
    'processing_time_ms': 165
}
```

### API Endpoint

```python
POST /predict/project/{project_id}

Response (JSON):
{
  "project_id": "PROJ-042",
  "predictions": {...},
  "confidence": 0.89,
  "explainability": {...}
}
```

**Response Time:** ~200ms per project

---

## 2️⃣ Batch Mode: Portfolio-Wide Analysis

### When to Use
- **Scheduled Runs**: Nightly/weekly portfolio scans
- **Monthly Reports**: Steering committee meetings
- **Quarterly Planning**: Portfolio rebalancing
- **Continuous Monitoring**: Detect emerging risks

### Workflow

```
Scheduler → Fetch All Projects → Batch Process → Store Results → Trigger Alerts
```

### Process Flow

```python
def batch_analyze_portfolio(schedule='nightly'):
    """
    Analyze all active projects in the portfolio
    """
    
    # 1. Fetch all active projects from PPM system
    projects = fetch_active_projects()
    # Returns: List of 50-250 active projects
    
    # 2. Determine processing order
    projects = prioritize_projects(projects)
    
    # 3. Process in batches
    batch_size = 10  # Process 10 projects at a time
    
    results = []
    for i in range(0, len(projects), batch_size):
        batch = projects[i:i+batch_size]
        
        # Parallel processing within batch
        batch_results = process_batch(batch)
        results.extend(batch_results)
        
        # Store intermediate results
        store_predictions(batch_results)
        
        # Check for critical alerts
        check_alerts(batch_results)
    
    # 4. Generate portfolio-level insights
    portfolio_summary = aggregate_results(results)
    
    # 5. Trigger notifications
    send_reports(portfolio_summary)
    
    return results
```

---

## 🎯 Project Processing Order

### Default Priority Order

Projects are processed in this order:

1. **Critical Projects** (Risk > 80 or Budget > $10M)
   - Highest business impact
   - Require immediate attention

2. **High-Value Projects** (NPV > $5M)
   - Strategic importance
   - Board-level visibility

3. **At-Risk Projects** (Previous risk score 60-80)
   - Monitor deterioration
   - Early warning system

4. **New Projects** (Started in last 30 days)
   - Establish baseline
   - Catch issues early

5. **Standard Projects** (All others)
   - Regular monitoring
   - Bulk processing

### Sorting Algorithm

```python
def prioritize_projects(projects):
    """
    Sort projects by priority for processing
    """
    def priority_score(project):
        score = 0
        
        # Factor 1: Previous risk score (40% weight)
        if project.get('previous_risk', 0) > 80:
            score += 400
        elif project.get('previous_risk', 0) > 60:
            score += 300
        
        # Factor 2: Budget size (30% weight)
        budget_m = project['budget'] / 1_000_000
        score += min(budget_m * 10, 300)
        
        # Factor 3: Strategic value (20% weight)
        score += project.get('strategic_value', 50) * 2
        
        # Factor 4: Time since last analysis (10% weight)
        days_since = (datetime.now() - project['last_analyzed']).days
        score += min(days_since * 2, 100)
        
        return score
    
    # Sort descending by priority
    return sorted(projects, key=priority_score, reverse=True)
```

### Example Priority Order

```
Processing Order for 50 Projects:
───────────────────────────────────────────────────────
1.  PROJ-015  Priority: 850  ($12M, Risk=85, Strategic)
2.  PROJ-042  Priority: 720  ($8M, Risk=68, High-Value)
3.  PROJ-031  Priority: 680  ($5M, Risk=72, At-Risk)
4.  PROJ-009  Priority: 620  (New, Started 5 days ago)
5.  PROJ-023  Priority: 580  ($4M, Risk=55)
...
48. PROJ-047  Priority: 120  ($500K, Risk=25, Stable)
49. PROJ-018  Priority: 110  ($400K, Risk=22, Green)
50. PROJ-033  Priority: 100  ($300K, Risk=18, Low)
```

---

## ⚡ Batch Processing Architecture

### Parallel Processing

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def process_batch(projects, max_workers=5):
    """
    Process multiple projects in parallel
    """
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all projects
        futures = {
            executor.submit(analyze_project, project): project
            for project in projects
        }
        
        # Collect results as they complete
        for future in as_completed(futures):
            project = futures[future]
            try:
                result = future.result(timeout=30)
                results.append(result)
            except Exception as e:
                log_error(f"Failed to process {project['id']}: {e}")
    
    return results

def analyze_project(project):
    """
    Run all 4 models on a single project
    """
    return {
        'project_id': project['id'],
        'timestamp': datetime.now(),
        'risk': PRM.predict(project),
        'cost': COP.predict(project),
        'success': SLM.predict(project),
        'priority': PO.score(project)
    }
```

### Processing Throughput

- **Single Project**: ~200ms
- **Batch of 10**: ~500ms (parallel processing)
- **Full Portfolio (100 projects)**: ~5-10 minutes

---

## 📅 Scheduled Processing

### Nightly Batch (Default)

```yaml
Schedule: 2:00 AM daily
Trigger: Cron job
Process: Full portfolio scan

Steps:
1. 02:00 - Fetch all active projects (100 projects)
2. 02:02 - Process critical projects (15 projects)
3. 02:04 - Process high-value projects (25 projects)
4. 02:06 - Process remaining projects (60 projects)
5. 02:10 - Generate portfolio summary
6. 02:12 - Store results in database
7. 02:15 - Send email alerts for critical risks
8. 02:16 - Update dashboard cache
9. 02:17 - Complete
```

### Weekly Deep Analysis

```yaml
Schedule: Sunday 3:00 AM
Trigger: Weekly cron
Process: Full portfolio + historical trends

Additional:
- Compare vs. last week
- Trend analysis (4-week rolling)
- Portfolio optimization run
- Executive summary report
```

### On-Demand Processing

```python
# Triggered by events
trigger_events = [
    'project_status_change',      # Status updated in PPM
    'milestone_missed',            # Milestone deadline passed
    'budget_update',               # Budget revised
    'team_change',                 # PM or team member changed
    'scope_change_approved'        # Major scope change
]

def event_triggered_analysis(event, project_id):
    """
    Immediate re-analysis when significant events occur
    """
    project = fetch_project_data(project_id)
    
    # Run models
    predictions = analyze_project(project)
    
    # Check if risk level changed significantly
    previous_risk = get_previous_risk(project_id)
    if abs(predictions['risk'] - previous_risk) > 15:
        # Alert if risk jumped >15 points
        send_alert(project_id, predictions)
    
    return predictions
```

---

## 🎯 Data Flow Example

### Morning Portfolio Analysis

```
06:00 AM - Executive Dashboard Opens
├─ Load cached predictions (from 2 AM run)
├─ Show portfolio health: 85% (↑2%)
├─ High-risk projects: 12 (↓3 from yesterday)
├─ Budget alerts: 5 projects over 15% variance
└─ Action items: 8 projects need intervention

08:30 AM - PMO Meeting
├─ PMO clicks on PROJ-042
├─ Real-time API call triggered
├─ Latest data fetched (as of 8:30 AM)
├─ Models re-run (200ms)
└─ Updated predictions displayed

10:00 AM - Gate Review for PROJ-015
├─ Real-time analysis requested
├─ All 4 models run with latest data
├─ Risk: 72 → "PROCEED WITH CONDITIONS"
└─ Decision logged, triggers retraining later

02:00 PM - Scope Change Approved for PROJ-023
├─ Event trigger fires
├─ Immediate re-analysis
├─ Risk: 55 → 68 (jumped 13 points)
├─ Alert sent to PM and PMO
└─ Added to tomorrow's deep-dive list
```

---

## 🔄 Model Update Frequency

### Project-Level
- **Real-time**: On-demand (200ms latency)
- **Nightly**: All active projects
- **Event-driven**: When significant changes occur

### Portfolio-Level
- **Daily**: Portfolio health score
- **Weekly**: Trend analysis
- **Monthly**: Full optimization run
- **Quarterly**: Strategic rebalancing

---

## 💾 Data Storage

### Prediction History

```sql
CREATE TABLE predictions (
    id BIGSERIAL PRIMARY KEY,
    project_id VARCHAR(50),
    timestamp TIMESTAMP,
    risk_score INTEGER,
    cost_variance FLOAT,
    success_probability FLOAT,
    priority_score INTEGER,
    model_version VARCHAR(20),
    processing_time_ms INTEGER
);

-- Index for fast lookups
CREATE INDEX idx_project_time ON predictions(project_id, timestamp DESC);
```

### Query Latest Predictions

```python
def get_latest_predictions(project_id):
    """
    Get most recent predictions for a project
    """
    query = """
        SELECT * FROM predictions
        WHERE project_id = %s
        ORDER BY timestamp DESC
        LIMIT 1
    """
    return db.execute(query, [project_id])

def get_prediction_history(project_id, days=30):
    """
    Get historical predictions for trend analysis
    """
    query = """
        SELECT * FROM predictions
        WHERE project_id = %s
          AND timestamp > NOW() - INTERVAL '%s days'
        ORDER BY timestamp ASC
    """
    return db.execute(query, [project_id, days])
```

---

## 🚨 Alert Workflow

### When Alerts Trigger

1. **Critical Risk (>80)**
   - Immediate Slack/email to C-level
   - Add to daily standup agenda
   - PMO owner assigned

2. **High Cost Variance (>15%)**
   - Email to CFO and sponsor
   - Financial review scheduled
   - Escalation path activated

3. **Success Probability Drop (<50%)**
   - Email to project sponsor
   - Recovery plan required within 48hrs
   - Executive steering meeting

---

## 📊 Performance Optimization

### Caching Strategy

```python
from functools import lru_cache
import redis

# Cache predictions for 1 hour
@lru_cache(maxsize=200)
def get_cached_prediction(project_id):
    """
    Return cached prediction if < 1 hour old
    Otherwise run fresh analysis
    """
    cache_key = f"prediction:{project_id}"
    cached = redis.get(cache_key)
    
    if cached and cache_age(cached) < 3600:
        return cached
    
    # Run fresh analysis
    fresh = analyze_project(project_id)
    redis.setex(cache_key, 3600, fresh)
    return fresh
```

---

## 🎯 Summary

**Processing Order:**
1. Critical projects first (risk/budget)
2. High-value projects second
3. At-risk projects third
4. New projects fourth
5. Standard projects last

**Processing Modes:**
- **Real-time**: One project, ~200ms
- **Batch**: Multiple projects, parallel
- **Scheduled**: Nightly portfolio scan

**Data Flow:**
```
Projects → Priority Queue → Models → Predictions → Storage → Alerts → Dashboard
```
