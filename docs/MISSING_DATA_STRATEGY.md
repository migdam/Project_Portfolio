# Missing Data Handling Strategy

## Overview

Portfolio ML systems often face incomplete project data due to:
- New projects with limited history
- Legacy projects with sparse documentation
- Inconsistent data collection across teams
- Integration gaps between PPM/Finance/HR systems

This document describes how the Portfolio ML system handles missing data to ensure reliable predictions even with incomplete information.

## Data Quality Framework

### Field Classification

**Required Fields** (Analysis cannot proceed without these):
- `project_id` - Unique identifier
- `risk_score` - Primary risk indicator

**Optional Fields** (Can be imputed if missing):
- `cost_variance` - Budget overrun percentage
- `success_probability` - Likelihood of success
- `budget` - Total project budget
- `team_size` - Number of team members
- `duration_months` - Project timeline

### Quality Levels

| Level | Completeness | Confidence Penalty | Can Analyze? |
|-------|--------------|-------------------|--------------|
| **HIGH** | ≥85% | 0% | ✅ Yes |
| **MEDIUM** | 30-84% | -15% | ✅ Yes |
| **LOW** | <30% | -35% | ❌ No (insufficient) |

### Minimum Threshold

**Analysis requires:**
- ✅ All required fields present
- ✅ At least 30% overall completeness

## Imputation Strategies

### 1. Historical Imputation (Preferred)

Uses historical data from the same project.

**Example:**
```python
# Project PROJ-042 missing current risk_score
# Look back 90 days and use median
historical_risks = [65, 68, 72, 75, 70]  # Last 5 data points
imputed_risk_score = 70  # Median

# Result: "Historical median (5 points)"
```

**Advantages:**
- ✅ Project-specific patterns
- ✅ Captures project trajectory
- ✅ Higher confidence

**When to use:**
- Project has 90-day history
- Similar data points available

### 2. Conservative Defaults

Uses safe assumptions that err on the side of caution.

**Default Values:**

| Field | Default | Rationale |
|-------|---------|-----------|
| `risk_score` | 50 | Assume medium risk (neutral) |
| `cost_variance` | +5% | Assume slight overrun (realistic) |
| `success_probability` | 70% | Neutral success rate |
| `budget` | $1M | Typical mid-size project |
| `team_size` | 5 | Average team size |
| `duration_months` | 6 | Standard project length |

**When to use:**
- New project with no history
- Historical data unavailable
- First-time analysis

### 3. Similar Project Imputation (Future Enhancement)

Uses data from similar projects based on:
- Risk score proximity
- Budget range
- Domain/industry
- Team size
- Organizational unit

**Status:** Placeholder (returns defaults for now)

**Future Implementation:**
```python
# Find 5 most similar projects
similar = find_similar_projects(
    risk_score=65,
    budget=2_000_000,
    domain="IT Infrastructure"
)

# Use median of similar projects
imputed_value = median([p.cost_variance for p in similar])
```

## Usage Examples

### Example 1: Complete Data (No Imputation)

```python
from missing_data_handler import MissingDataHandler
from database import PortfolioDB

db = PortfolioDB("portfolio_predictions.db")
handler = MissingDataHandler(db)

project_data = {
    'project_id': 'PROJ-042',
    'risk_score': 65,
    'cost_variance': 12.5,
    'success_probability': 0.82,
    'budget': 5000000,
    'team_size': 8,
    'duration_months': 12
}

result = handler.analyze_with_missing_data(project_data, verbose=True)
```

**Output:**
```
📊 Data Quality Assessment
   Completeness: 100.0%
   Quality Level: HIGH
   Missing Fields: 0

Status: SUCCESS
Quality: HIGH
Confidence Penalty: 0%
```

---

### Example 2: Partial Data (Imputation Needed)

```python
project_data = {
    'project_id': 'PROJ-103',
    'risk_score': 75,
    'cost_variance': 18.3
    # Missing: success_probability, budget, team_size, duration_months
}

result = handler.analyze_with_missing_data(project_data, verbose=True)
```

**Output:**
```
📊 Data Quality Assessment
   Completeness: 42.9%
   Quality Level: MEDIUM
   Missing Fields: 4
   → success_probability, budget, team_size, duration_months

🔧 Imputed 4 fields:
   success_probability: Neutral default (70%)
   budget: Similar projects or default ($1M)
   team_size: Similar projects or default (5)
   duration_months: Similar projects or default (6 months)

Status: SUCCESS
Quality: MEDIUM
Warnings:
  ⚠️  MEDIUM data quality (43% complete) - confidence reduced by 15%
  ⚠️  4 fields imputed - verify data source completeness
```

---

### Example 3: Insufficient Data (Cannot Analyze)

```python
project_data = {
    'project_id': 'PROJ-INSUFFICIENT',
    'cost_variance': 10.0
    # Missing: risk_score (REQUIRED!)
}

result = handler.analyze_with_missing_data(project_data, verbose=True)
```

**Output:**
```
📊 Data Quality Assessment
   Completeness: 28.6%
   Quality Level: LOW
   Missing Fields: 5
   → risk_score, success_probability, budget, team_size, duration_months

Status: INSUFFICIENT_DATA
Message: Cannot analyze: 1 required fields missing
Required Fields Missing: ['risk_score']
```

---

### Example 4: Integration with Agent

```python
from langgraph_agent import PortfolioAgent
from missing_data_handler import MissingDataHandler
from database import PortfolioDB

db = PortfolioDB("portfolio_predictions.db")
handler = MissingDataHandler(db)
agent = PortfolioAgent(use_llm=False, db_path="portfolio_predictions.db")

# Project with missing data
project_data = {
    'project_id': 'PROJ-205',
    'risk_score': 68
    # Missing optional fields
}

# Step 1: Handle missing data
data_result = handler.analyze_with_missing_data(project_data)

if data_result['status'] == 'SUCCESS':
    # Step 2: Use imputed data for analysis
    imputed_data = data_result['imputed_data']
    
    # Step 3: Adjust confidence based on data quality
    quality = data_result['quality']
    
    # Store prediction with quality metadata
    db.store_prediction(
        project_id=imputed_data['project_id'],
        risk_score=imputed_data['risk_score'],
        cost_variance=imputed_data['cost_variance'],
        success_probability=imputed_data['success_probability'],
        metadata={
            'data_quality': quality['quality_level'],
            'completeness': quality['completeness'],
            'imputed_fields': list(data_result['imputation_log'].keys())
        }
    )
    
    # Display warnings to user
    for warning in data_result['warnings']:
        print(warning)
else:
    print(f"❌ {data_result['message']}")
```

## Portfolio Data Quality Report

### Generate Report

```python
handler = MissingDataHandler(db)
report = handler.get_portfolio_data_quality_report(hours=720)  # Last 30 days

print(f"Total Projects: {report['total_projects']}")
print(f"Overall Portfolio Health: {report['overall_portfolio_health']}")
```

### Report Components

**1. Quality Distribution**
```
Quality Distribution:
  HIGH: 15 (35.7%)
  MEDIUM: 20 (47.6%)
  LOW: 5 (11.9%)
  INSUFFICIENT: 2 (4.8%)
```

**2. Most Commonly Missing Fields**
```
Most Commonly Missing Fields:
  budget: 35 projects
  team_size: 32 projects
  duration_months: 28 projects
```

**3. Projects Needing Improvement**
```
Projects Needing Data Improvement (Top 5):
  PROJ-142: LOW (28% complete)
  PROJ-089: MEDIUM (42% complete)
  PROJ-205: MEDIUM (57% complete)
```

**4. Overall Portfolio Health**

| Health | Criteria |
|--------|----------|
| **EXCELLENT** | ≥85% projects with HIGH quality |
| **GOOD** | ≥70% projects with HIGH quality |
| **FAIR** | <70% HIGH, <20% INSUFFICIENT |
| **POOR** | >20% projects with INSUFFICIENT data |

## Confidence Adjustment

Predictions are adjusted based on data quality:

```python
# Base confidence from model
base_confidence = 0.85

# Adjust for data quality
quality = handler.assess_data_quality(project_data)
adjusted_confidence = base_confidence * (1 - quality['confidence_penalty'])

# Examples:
# HIGH quality (0% penalty): 0.85 * (1 - 0.00) = 0.85 (85%)
# MEDIUM quality (15% penalty): 0.85 * (1 - 0.15) = 0.72 (72%)
# LOW quality (35% penalty): 0.85 * (1 - 0.35) = 0.55 (55%)
```

### Display to User

```python
print(f"Risk Score: {risk_score}")
print(f"Confidence: {adjusted_confidence:.1%}")
print(f"Data Quality: {quality['quality_level']}")

if quality['quality_level'] != 'HIGH':
    print(f"⚠️  Confidence reduced by {quality['confidence_penalty']:.0%} due to missing data")
```

## Best Practices

### ✅ DO:

1. **Always check data quality first**
   ```python
   result = handler.analyze_with_missing_data(project_data)
   if result['status'] != 'SUCCESS':
       return error_response(result['message'])
   ```

2. **Display warnings to users**
   ```python
   for warning in result['warnings']:
       ui.show_warning(warning)
   ```

3. **Track imputation in metadata**
   ```python
   db.store_prediction(
       ...,
       metadata={
           'imputed_fields': list(imputation_log.keys()),
           'data_quality': quality_level
       }
   )
   ```

4. **Generate regular data quality reports**
   ```python
   # Weekly report to identify data gaps
   report = handler.get_portfolio_data_quality_report(hours=168)
   send_to_pmo(report)
   ```

5. **Improve data collection for frequently missing fields**
   ```python
   # Target top missing fields for process improvement
   top_missing = report['top_missing_fields']
   ```

### ❌ DON'T:

1. **Don't analyze without checking data quality**
   ```python
   # BAD: Blindly use incomplete data
   result = agent.analyze(project_id)
   
   # GOOD: Check quality first
   data_result = handler.analyze_with_missing_data(project_data)
   if data_result['status'] == 'SUCCESS':
       result = agent.analyze(project_id)
   ```

2. **Don't hide data quality from users**
   ```python
   # BAD: Show prediction without quality context
   print(f"Risk: {risk_score}")
   
   # GOOD: Show quality context
   print(f"Risk: {risk_score} (Data Quality: {quality_level})")
   ```

3. **Don't use imputed data without logging**
   ```python
   # BAD: Silent imputation
   if 'budget' not in project_data:
       project_data['budget'] = 1000000
   
   # GOOD: Log and track imputation
   result = handler.impute_missing_values(project_data)
   imputed_data = result[0]
   imputation_log = result[1]  # Track what was imputed
   ```

4. **Don't ignore data quality trends**
   ```python
   # Monitor portfolio health over time
   report_week1 = handler.get_portfolio_data_quality_report(hours=168)
   report_week2 = handler.get_portfolio_data_quality_report(hours=168)
   
   if report_week2['overall_portfolio_health'] < report_week1['overall_portfolio_health']:
       alert_pmo("Data quality degrading")
   ```

## Integration Points

### 1. LangGraph Agent Integration

```python
# In langgraph_agent.py - analyze_project node
def analyze_project(self, state: AgentState) -> AgentState:
    project_id = state["project_id"]
    
    # Fetch data
    project_data = self.db.get_predictions(project_id=project_id, hours=1)[0]
    
    # Handle missing data
    handler = MissingDataHandler(self.db)
    data_result = handler.analyze_with_missing_data(project_data)
    
    if data_result['status'] == 'INSUFFICIENT_DATA':
        # Escalate to human
        state['needs_human_review'] = True
        state['messages'].append(
            AIMessage(content=f"⚠️ Cannot analyze {project_id}: {data_result['message']}")
        )
        return state
    
    # Use imputed data
    state['project_data'] = data_result['imputed_data']
    state['data_quality'] = data_result['quality']
    
    # Add warnings to state
    for warning in data_result['warnings']:
        state['messages'].append(AIMessage(content=warning))
    
    return state
```

### 2. Real-Time Dashboard Integration

```python
# In realtime_dashboard_db.py
def display_project_with_quality(project_id):
    handler = MissingDataHandler(db)
    project_data = db.get_predictions(project_id=project_id, hours=1)[0]
    
    result = handler.analyze_with_missing_data(project_data)
    
    if result['status'] == 'SUCCESS':
        quality = result['quality']
        
        # Color-code by quality
        quality_colors = {
            'HIGH': 'green',
            'MEDIUM': 'orange',
            'LOW': 'red'
        }
        
        st.metric(
            label=f"{project_id} - Risk Score",
            value=result['imputed_data']['risk_score'],
            delta=f"Data Quality: {quality['quality_level']}",
            delta_color=quality_colors[quality['quality_level']]
        )
        
        # Show warnings
        for warning in result['warnings']:
            st.warning(warning)
    else:
        st.error(f"Cannot analyze {project_id}: {result['message']}")
```

### 3. Batch Processing Integration

```python
# Process entire portfolio with missing data handling
def batch_process_with_missing_data():
    handler = MissingDataHandler(db)
    recent = db.get_predictions(hours=24)
    
    results = []
    skipped = []
    
    for pred in recent:
        project_data = {
            'project_id': pred['project_id'],
            'risk_score': pred['risk_score'],
            'cost_variance': pred.get('cost_variance'),
            'success_probability': pred.get('success_probability')
        }
        
        data_result = handler.analyze_with_missing_data(project_data)
        
        if data_result['status'] == 'SUCCESS':
            results.append({
                'project_id': pred['project_id'],
                'data': data_result['imputed_data'],
                'quality': data_result['quality']
            })
        else:
            skipped.append(pred['project_id'])
    
    print(f"Processed: {len(results)}, Skipped: {len(skipped)}")
    return results, skipped
```

## Monitoring & Alerts

### Alert Thresholds

```python
def check_data_quality_alerts(report):
    alerts = []
    
    # Alert 1: Portfolio health degraded
    if report['overall_portfolio_health'] in ['POOR', 'FAIR']:
        alerts.append({
            'severity': 'HIGH',
            'message': f"Portfolio data health is {report['overall_portfolio_health']}"
        })
    
    # Alert 2: Too many projects with insufficient data
    insufficient_pct = report['quality_percentage']['INSUFFICIENT']
    if insufficient_pct > 10:
        alerts.append({
            'severity': 'HIGH',
            'message': f"{insufficient_pct:.1f}% of projects have insufficient data"
        })
    
    # Alert 3: Specific field consistently missing
    for field, count in report['top_missing_fields']:
        if count > report['total_projects'] * 0.5:
            alerts.append({
                'severity': 'MEDIUM',
                'message': f"Field '{field}' missing in {count} projects (50%+)"
            })
    
    return alerts
```

## Future Enhancements

### 1. Machine Learning-Based Imputation

Train models to predict missing values based on other features:

```python
# Train imputation model
from sklearn.ensemble import RandomForestRegressor

def train_imputation_model(field_name, historical_data):
    """Train ML model to impute specific field"""
    # Features: other available fields
    # Target: missing field
    pass
```

### 2. Similarity-Based Imputation

Find truly similar projects for better imputation:

```python
def find_similar_projects(project_data, top_k=5):
    """
    Use vector similarity to find similar projects
    - Embedding: [risk_score, budget, team_size, ...]
    - Metric: Cosine similarity
    """
    pass
```

### 3. Time-Series Forecasting

Predict next values based on project trajectory:

```python
def forecast_missing_value(project_id, field_name):
    """Use ARIMA/LSTM to forecast based on trend"""
    pass
```

### 4. Multi-Imputation

Generate multiple plausible values and quantify uncertainty:

```python
def multiple_imputation(project_data, n_imputations=5):
    """
    Generate multiple imputed datasets
    Analyze with each
    Aggregate results with uncertainty bands
    """
    pass
```

## Summary

The Missing Data Handler provides:

- ✅ **Data Quality Assessment** - 3-tier quality levels (HIGH/MEDIUM/LOW)
- ✅ **Multiple Imputation Strategies** - Historical, conservative defaults, similar projects
- ✅ **Confidence Adjustment** - Predictions penalized for low data quality
- ✅ **User Warnings** - Clear communication about data limitations
- ✅ **Portfolio Reports** - Identify data gaps across entire portfolio
- ✅ **Graceful Degradation** - Continues analysis even with missing data (when possible)

**Key Principle:** Transparency over perfection. Always inform users about data quality and imputation methods used.
