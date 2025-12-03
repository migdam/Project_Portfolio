# 🔧 How It Works

This document explains the architecture, workflows, and technical implementation of the Portfolio ML system.

---

## System Architecture

### Overview

Portfolio ML is a complete MLOps platform that predicts project outcomes and optimizes portfolio decisions using machine learning. The system follows a microservices architecture with clear separation between data ingestion, model training, inference, and monitoring.

```
┌─────────────────────────────────────────────────────────────────┐
│                         Data Sources                             │
│  PPM Systems │ Finance │ HR/Resources │ Risk Logs │ Jira/Azure  │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data Pipeline                               │
│  ┌──────────┐  ┌──────────┐  ┌────────────┐  ┌──────────────┐ │
│  │ Ingest   │→ │Transform │→ │  Validate  │→ │Feature Store │ │
│  └──────────┘  └──────────┘  └────────────┘  └──────────────┘ │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                      ML Core (4 Models)                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │   PRM    │  │   COP    │  │   SLM    │  │      PO       │  │
│  │  Risk    │  │   Cost   │  │ Success  │  │  Optimizer    │  │
│  │Predictor │  │Predictor │  │Predictor │  │   (Pareto)    │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └───────┬───────┘  │
│       └─────────────┴──────────────┴─────────────────┘          │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                   API & Interfaces                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │
│  │ FastAPI  │  │Streamlit │  │WebSocket │  │   Webhooks   │   │
│  │REST API  │  │Dashboard │  │Real-time │  │  Callbacks   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────┘   │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MLOps & Monitoring                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │
│  │  Drift   │  │Feedback  │  │A/B Tests │  │   Alerting   │   │
│  │Detection │  │  Loop    │  │  Live    │  │Multi-channel │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. Data Pipeline

**Data Ingestion**
- Connects to PPM systems (Jira, Azure DevOps, MS Project)
- Pulls financial data (budgets, actuals, forecasts)
- Imports resource data (team composition, skills, utilization)
- Collects risk logs and issue tracking data

**Data Validation**
- Uses Great Expectations for data quality checks
- Validates completeness (≥85% threshold)
- Checks schema compliance
- Detects anomalies and outliers

**Feature Engineering**
- **Feature Store**: Centralized feature registry with versioning
- **Computed Features**:
  - Velocity trends (completed/planned tasks ratio)
  - Scope change rate (changes per month)
  - Burn rate variance (actual vs planned)
  - Team experience score (weighted by stability)
  - Dependency risk (external dependencies × vendor risk)

**Workflow:**
```python
# 1. Extract data from sources
raw_data = extract_from_ppm_system()

# 2. Validate data quality
validation_results = validate_data(raw_data)

# 3. Transform and engineer features
features = feature_store.compute_features(
    raw_data,
    feature_group="prm_features"
)

# 4. Store for training/inference
feature_store.materialize_features(features)
```

---

### 2. ML Models

#### Project Risk Model (PRM)
**Purpose**: Predict schedule slippage, budget overruns, and resource bottlenecks

**How it works:**
1. Takes project attributes (budget, duration, team size, complexity)
2. Computes velocity trends and scope change patterns
3. Uses XGBoost classifier to predict risk level (LOW/MEDIUM/HIGH)
4. Outputs risk score (0-100) with confidence interval

**Key Features Used:**
- Milestone variance
- Scope change frequency
- Team experience
- Burn rate trends
- Dependency complexity

**Output:**
```json
{
  "risk_level": "HIGH",
  "risk_score": 75,
  "confidence": 0.89,
  "top_factors": [
    {"feature": "scope_changes", "impact": 0.32},
    {"feature": "milestone_variance", "impact": 0.28}
  ]
}
```

#### Cost Overrun Predictor (COP)
**Purpose**: Forecast budget overruns before they happen

**How it works:**
1. Analyzes historical cost patterns
2. Tracks burn rate against planned budget
3. Considers scope changes and resource allocation
4. Predicts final cost with confidence bands

**Key Features:**
- Burn rate variance
- Scope change impact
- Resource utilization
- Vendor dependencies

**Output:**
```json
{
  "predicted_overrun_pct": 12.5,
  "predicted_final_cost": 1125000,
  "confidence": 0.84,
  "risk_factors": ["high_scope_changes", "resource_constraints"]
}
```

#### Success Likelihood Model (SLM)
**Purpose**: Estimate probability of project success

**How it works:**
1. Learns from historical project outcomes
2. Considers team capabilities and project complexity
3. Evaluates governance and stakeholder engagement
4. Outputs success probability (0-1)

**Key Features:**
- Team experience and stability
- Project complexity score
- Stakeholder engagement
- Governance compliance

**Output:**
```json
{
  "success_probability": 0.853,
  "confidence": 0.91,
  "key_factors": [
    "Strong team experience",
    "Stable scope",
    "Good resource planning"
  ]
}
```

#### Portfolio Optimizer (PO)
**Purpose**: Select optimal project mix given constraints

**How it works:**
1. Evaluates all candidate projects
2. Computes strategic value vs risk trade-offs
3. Applies constraints (budget, resources, dependencies)
4. Uses Pareto frontier optimization
5. Recommends best project portfolio

**Optimization Criteria:**
- Maximize strategic value
- Minimize portfolio risk
- Respect budget constraints
- Balance resource allocation

**Output:**
```json
{
  "selected_projects": ["PROJ-001", "PROJ-005", "PROJ-012"],
  "total_value": 45.2,
  "avg_risk": 34,
  "budget_utilization": 0.92,
  "pareto_optimal": true
}
```

---

### 3. Real-Time Features

#### WebSocket Notifications
**How it works:**
1. Clients connect via WebSocket (`ws://api/ws/{client_id}`)
2. Subscribe to channels (predictions, alerts, model_updates)
3. Receive instant notifications when events occur
4. Server maintains connection pool with auto-reconnect

**Use Cases:**
- Live risk alerts when project risk increases
- Real-time prediction updates
- Model deployment notifications
- Drift detection alerts

**Example:**
```javascript
// Client connects and subscribes
ws.send(JSON.stringify({
  action: "subscribe",
  channel: "alerts"
}));

// Receive real-time alert
ws.onmessage = (event) => {
  const alert = JSON.parse(event.data);
  // { type: "risk_alert", project_id: "PROJ-001", risk_level: "HIGH" }
};
```

#### A/B Testing
**How it works:**
1. Define experiment with 2+ model variants
2. Split traffic (e.g., 50% model A, 50% model B)
3. Track performance metrics for each variant
4. Statistical analysis determines winner
5. Promote winning variant to production

**Traffic Splitting:**
- Uses consistent hashing for user-based assignment
- Ensures same user always sees same variant
- Configurable traffic percentages

**Example:**
```python
# Create experiment
experiment = ab_test_manager.create_experiment(
    experiment_id="prm_v2_test",
    model_name="PRM",
    variants=[
        ModelVariant("v1", "models/prm_v1.pkl", 50.0, "Current model"),
        ModelVariant("v2", "models/prm_v2.pkl", 50.0, "New XGBoost model")
    ],
    success_metric="accuracy"
)

# Get variant for request
variant = ab_test_manager.get_variant_for_request(
    "prm_v2_test",
    user_id="user_123"
)

# Record results
ab_test_manager.record_result(
    "prm_v2_test",
    variant.variant_id,
    accuracy=0.91,
    latency_ms=45.2
)

# Determine winner
winner = ab_test_manager.get_winner("prm_v2_test")
```

---

### 4. MLOps Capabilities

#### Drift Detection
**How it works:**
1. Monitors incoming prediction data
2. Compares feature distributions to training data
3. Uses statistical tests (KS test, PSI)
4. Alerts when drift exceeds threshold
5. Triggers retraining workflow

**Detection Methods:**
- Feature drift (input data changes)
- Prediction drift (output distribution changes)
- Performance drift (accuracy degradation)

#### Feedback Loop
**How it works:**
1. Users rate predictions (1-5 stars)
2. Provide corrections for wrong predictions
3. System logs actual outcomes
4. Analyzes feedback for patterns
5. Generates retraining datasets

**Continuous Improvement:**
```python
# Record feedback
feedback_collector.record_feedback(
    prediction_id="pred_123",
    model_name="PRM",
    predicted_value=75,
    actual_value=82,  # Actual outcome
    user_rating=4,
    feedback_type="validation"
)

# Analyze for improvements
analyzer = FeedbackAnalyzer(feedback_collector)
recommendations = analyzer.recommend_model_improvements("PRM")

# Generate retraining data
retraining_data = analyzer.generate_retraining_dataset("PRM")
```

#### Data Lineage
**How it works:**
1. Tracks every data transformation
2. Records model training events
3. Links predictions to source data
4. Creates ancestry graph
5. Enables compliance audits

**Lineage Tracking:**
```python
# Record data flow
lineage_tracker.record_data_source("src_001", "PPM Extract", "database")
lineage_tracker.record_transformation("transform_001", "Feature Engineering", ["src_001"])
lineage_tracker.record_model_training("model_prm_v2", "PRM", ["transform_001"], hyperparams, metrics)
lineage_tracker.record_prediction("pred_123", "model_prm_v2", "input_456", 75, 0.89)

# Retrieve full lineage
lineage = lineage_tracker.get_lineage("pred_123")
# Shows: source → transformation → model → prediction
```

---

### 5. Security & Multi-Tenancy

#### Authentication
**JWT-based authentication:**
1. User logs in with credentials
2. Server issues JWT token (1 hour expiry)
3. Client includes token in API requests
4. Server validates token signature and expiry

**Rate Limiting:**
- Token bucket algorithm
- 100 requests per minute per user
- Prevents API abuse
- Returns 429 status when exceeded

#### Multi-Tenancy
**How it works:**
1. Each organization gets unique tenant_id
2. All data queries filtered by tenant_id
3. Subscription tiers control feature access
4. Data isolation at database level

**Subscription Tiers:**
- **Free**: 10 projects, PRM + COP models, 1K API calls/day
- **Professional**: 100 projects, PRM + COP + SLM + A/B testing, 50K calls/day
- **Enterprise**: Unlimited projects, all features, unlimited calls

---

## Deployment Workflow

### Kubernetes Deployment
**How it works:**
1. Package application as Docker container
2. Push to container registry
3. Apply Kubernetes manifests
4. K8s creates pods across cluster
5. Load balancer distributes traffic
6. Horizontal autoscaling based on CPU/memory

**Auto-scaling:**
```yaml
# Scale 2-10 replicas based on load
minReplicas: 2
maxReplicas: 10
metrics:
  - CPU: 70% threshold
  - Memory: 80% threshold
```

**Rolling Updates:**
- Zero-downtime deployments
- Health checks ensure pod readiness
- Automatic rollback on failure

---

## Integration Points

### PPM System Integration
**Supported Systems:**
- Jira (REST API)
- Azure DevOps (REST API)
- MS Project Server (SOAP/REST)
- Smartsheet (REST API)

**Data Sync:**
- Scheduled daily/weekly extracts
- Real-time webhooks for critical changes
- Incremental updates for efficiency

### Finance System Integration
**Data Required:**
- Project budgets and actuals
- Cost center allocations
- Vendor invoices
- Resource costs

**Integration Methods:**
- Direct database queries
- CSV/Excel file imports
- REST API connections
- SFTP file transfers

---

## Monitoring & Alerts

### Alert Channels
**Slack Integration:**
- Color-coded by severity
- Rich formatting with project details
- Interactive buttons for actions

**PagerDuty Integration:**
- Critical alerts trigger incidents
- On-call rotation support
- Escalation policies
- Incident acknowledgment

**Custom Webhooks:**
- POST JSON payload to any URL
- Integrate with internal systems
- Custom alert formatting

### Alert Types
1. **Risk Alerts**: Project risk exceeds threshold
2. **Drift Alerts**: Model performance degrading
3. **System Alerts**: API errors, downtime
4. **Model Updates**: Training completed, new version deployed

---

## Performance Characteristics

### API Latency
- Single prediction: 20-50ms
- Batch predictions: 100-500ms (100 projects)
- Portfolio optimization: 1-3s (500 projects)

### Throughput
- 1000+ predictions per second per instance
- Horizontal scaling for higher loads
- Async processing for batch jobs

### Model Accuracy
- PRM: 89% accuracy
- COP: 82% R² score
- SLM: 91% AUC-ROC
- PO: Pareto-optimal solutions

### Storage Requirements
- Models: ~100MB each
- Features: ~1GB per 10K projects
- Logs: ~10GB per month
- Backups: 2x active data

---

## Best Practices

### Model Training
1. Use at least 2-3 years of historical data
2. Ensure ≥85% data completeness
3. Balance training data (stratified sampling)
4. Cross-validate with 5 folds
5. Test on held-out data (20%)

### Feature Engineering
1. Register features in feature store
2. Version all transformations
3. Document feature definitions
4. Monitor feature importance
5. Remove stale/unused features

### Production Deployment
1. A/B test new models before full rollout
2. Monitor performance for 2 weeks
3. Keep previous version as fallback
4. Document deployment changes
5. Run smoke tests post-deployment

### Data Quality
1. Validate all inputs before prediction
2. Handle missing values gracefully
3. Cap extreme outliers
4. Log data quality issues
5. Alert on validation failures

---

## Troubleshooting

### Common Issues

**High Prediction Latency**
- Check model size (optimize if >500MB)
- Enable prediction caching
- Use batch prediction for multiple requests
- Scale horizontally (add more pods)

**Model Drift Detected**
- Analyze feature distributions
- Check for data source changes
- Retrain model with recent data
- Update feature transformations if needed

**Low Accuracy**
- Review feedback and error patterns
- Check for systematic biases
- Add more training data
- Tune hyperparameters
- Consider ensemble methods

**API Rate Limits**
- Upgrade subscription tier
- Implement request batching
- Cache frequent predictions
- Use WebSocket for real-time updates

---

## Next Steps

After understanding how the system works:

1. **Setup**: Follow [INSTALLATION.md](INSTALLATION.md) to deploy
2. **Configuration**: Customize models in `config/config.yaml`
3. **Integration**: Connect your PPM and finance systems
4. **Training**: Run initial model training with historical data
5. **Deployment**: Deploy to production and enable monitoring
6. **Optimization**: Use A/B testing and feedback loop for continuous improvement

For detailed implementation guides, see the `/docs` directory.
