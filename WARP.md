# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

**AI-Powered Project & Portfolio Machine Learning Models**

This repository contains ML models that enhance Portfolio Prioritization, Project Risk Detection, and Outcome Predictability for Project Portfolio Management (PPM). The system augments human decision-making with data-driven insights to maximize value, minimize risk, and learn from delivery data.

### Core ML Models

1. **Project Risk Model (PRM)** - Predicts schedule slippage, budget overruns, and resource bottlenecks
2. **Cost Overrun Predictor (COP)** - Forecasts probability and magnitude of cost overruns
3. **Success Likelihood Model (SLM)** - Estimates project success probability based on historical patterns
4. **Portfolio Optimizer (PO)** - Recommends optimal project sets given constraints and value indicators

### Key Objectives

- Improve investment decision accuracy (+25%)
- Detect risks earlier (-40% lead time)
- Reduce portfolio waste (+15% throughput)
- Optimize capital allocation (+10-20% value/cost ratio)

## Development Environment

- **Shell**: zsh 5.9
- **Platform**: macOS
- **Package Manager**: conda (for Python environments)
- **Development Workflow**: Uses `run.sh` scripts for common tasks

### Technology Stack

**ML Framework**
- Python with scikit-learn, XGBoost, and LSTM variants
- LangGraph for self-healing agent pipelines (automated retraining + monitoring)

**Data Layer**
- SQL databases for PPM and finance data extracts
- Minimum 2-3 years historical data required
- Data quality requirement: ≥85% completeness for schedule/cost fields

**Deployment**
- Docker/Kubernetes (Dev → Test → Prod)
- CI/CD with automated testing and model performance tracking
- Automated drift detection and retraining (90-day cycle minimum)

**Integration Points**
- PPM Tool (milestones, gates, scope changes, statuses)
- Finance systems (budgets, actuals, NPV)
- HR/Resource systems (capabilities, utilization)
- Operational risk/issue logs

## Model Development Workflow

### Training a Model

```bash
# Activate conda environment
conda activate project_portfolio

# Train specific model
python -m models.train --model prm --data data/historical_projects.csv
python -m models.train --model cop --data data/cost_history.csv
python -m models.train --model slm --data data/success_outcomes.csv
python -m models.train --model po --data data/portfolio_constraints.csv
```

### Running Tests

```bash
# Run all tests
./run.sh test

# Run specific model tests
pytest tests/models/test_prm.py
pytest tests/models/test_cop.py
pytest tests/models/test_slm.py
pytest tests/models/test_po.py

# Run data validation tests
pytest tests/data/test_quality.py
```

### Model Evaluation

```bash
# Generate model performance reports
python -m evaluation.metrics --model prm --output reports/

# Check for model drift
python -m monitoring.drift_detection --model all

# Run explainability analysis (SHAP values)
python -m explainability.analyze --model prm --project-id 12345
```

### Deployment

```bash
# Build Docker image
docker build -t portfolio-ml:latest .

# Run locally
docker-compose up

# Deploy to staging
./run.sh deploy --env staging

# Deploy to production (requires approval)
./run.sh deploy --env production
```

## Architecture Patterns

### Model Pipeline Structure

```
data/
├── raw/              # Original PPM/finance extracts
├── processed/        # Cleaned, feature-engineered data
└── validated/        # Quality-checked, ready for training

models/
├── prm/              # Project Risk Model
├── cop/              # Cost Overrun Predictor
├── slm/              # Success Likelihood Model
└── po/               # Portfolio Optimizer

pipeline/
├── ingestion/        # Data extraction and loading
├── preprocessing/    # Feature engineering and cleaning
├── training/         # Model training orchestration
├── evaluation/       # Model validation and metrics
└── deployment/       # Model serving and monitoring
```

### Feature Engineering Principles

- **Temporal features**: Velocity trends, milestone variance, phase duration
- **Complexity indicators**: Scope change frequency, dependency count, vendor risk
- **Historical patterns**: Team experience, similar project outcomes, organizational capacity
- **Financial metrics**: EV/PV ratios, burn rate variance, budget utilization
- **Risk signals**: Issue escalation patterns, stakeholder engagement, governance compliance

### Model Explainability Requirements

**All predictions must include**:
1. Risk score (0-100) or probability
2. Confidence interval
3. Top 5 contributing factors (SHAP values)
4. Trend indicators (improving/degrading)
5. Actionable recommendations

### Data Quality Gates

**Pre-training validation**:
- Check completeness thresholds (≥85%)
- Validate standardized status codes
- Verify historical data window (2-3 years)
- Detect and handle outliers
- Balance class distributions for classification models

**Post-training validation**:
- Cross-validation performance (5-fold minimum)
- Holdout test set evaluation
- Fairness and bias checks
- Performance consistency across project types

## Integration Guidelines

### Dashboard Integration

- Models expose REST API endpoints for real-time predictions
- Batch predictions for portfolio-level optimization
- Results cached with TTL based on data freshness
- Confidence scores displayed alongside predictions

### Governance Checkpoints

- **Gate Reviews**: AI risk insight box with trend analysis and triggers
- **Monthly Steering**: Top 10 concerns + Top 10 opportunities
- **Portfolio Planning**: Optimization recommendations with impact graphs
- **Project Cards**: Risk badges with expandable explanations

### Human Override Protocol

- All AI recommendations are advisory, not mandatory
- Users can document override reasons
- Override patterns feed back into model improvement
- Governance maintains final decision authority

## MLOps and Monitoring

### Continuous Monitoring

```bash
# Check model health
python -m monitoring.health_check

# View prediction distribution
python -m monitoring.prediction_stats --days 30

# Alert on performance degradation
python -m monitoring.alerts --threshold 0.05
```

### Retraining Triggers

- **Scheduled**: Every 90 days minimum
- **Performance-based**: When accuracy drops >5%
- **Data drift**: When feature distributions shift significantly
- **Business change**: New delivery processes, organizational changes

### Experiment Tracking

- Log all training runs with hyperparameters
- Version control for datasets and models
- A/B testing for model updates
- Rollback capability for production models

## Version Control

- **VCS**: Git
- **CLI Tool**: GitHub CLI (`gh`) is available for repository operations
- **Branching Strategy**: Feature branches for model development, main for production
- **Model Versioning**: Semantic versioning (e.g., prm-v2.1.3)

## MCP Integration

When working in this repository, prefer MCP tools for:
- File operations (reading/writing)
- Database operations (SQLite for local testing)
- Version control (Git)
- API interactions (HTTP for PPM/finance systems)

## Rollout Phases

**Phase 1 — Pilot (Months 1-3)**
- 10-20 live projects
- Risk model (PRM) only
- Validation and feedback collection

**Phase 2 — Scale (Months 4-6)**
- All priority portfolios
- Add COP and SLM models
- Dashboard integration

**Phase 3 — Optimization (Months 7-12)**
- Portfolio Optimizer (PO)
- Scenario simulation
- Full MLOps automation

## Key Success Metrics

- Prediction accuracy for each model (track over time)
- Early warning lead time (days before issue surfaces)
- Portfolio throughput efficiency (project velocity)
- Value/cost ratio improvement
- Governance gate adherence
- User adoption and trust scores
