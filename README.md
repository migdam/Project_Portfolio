# Portfolio ML - AI-Powered Project & Portfolio Machine Learning Models

ML models that enhance Portfolio Prioritization, Project Risk Detection, and Outcome Predictability for Project Portfolio Management (PPM).

## Features

- **Project Risk Model (PRM)** - Predicts schedule slippage, budget overruns, and resource bottlenecks
- **Cost Overrun Predictor (COP)** - Forecasts probability and magnitude of cost overruns
- **Success Likelihood Model (SLM)** - Estimates project success probability
- **Portfolio Optimizer (PO)** - Recommends optimal project portfolio selection

## Quick Start

### Setup

```bash
# Create and activate conda environment
conda create -n project_portfolio python=3.10
conda activate project_portfolio

# Install dependencies
./run.sh setup
```

### Training Models

```bash
# Train Project Risk Model
./run.sh train prm data/processed/projects.csv

# Train Cost Overrun Predictor
./run.sh train cop data/processed/financials.csv

# Train Success Likelihood Model
./run.sh train slm data/processed/projects.csv
```

### Running Tests

```bash
./run.sh test
```

### Deployment

```bash
# Build and run with Docker Compose
docker-compose up

# Access MLflow UI
open http://localhost:5000

# Access API
open http://localhost:8000/docs
```

## Project Structure

```
├── config/             # Configuration files
├── data/              # Data directories (raw, processed, validated)
├── models/            # ML model implementations
│   ├── prm.py        # Project Risk Model
│   ├── cop.py        # Cost Overrun Predictor
│   ├── slm.py        # Success Likelihood Model
│   └── po.py         # Portfolio Optimizer
├── pipeline/          # Data pipeline (ingestion, preprocessing, validation)
├── monitoring/        # MLOps monitoring (drift detection, health checks)
├── utils/             # Utility functions
├── tests/             # Test suite
└── run.sh            # Automation script
```

## Data Requirements

- **Minimum historical data**: 2-3 years of project delivery data
- **Completeness threshold**: ≥85% for schedule and cost fields
- **Required data sources**:
  - PPM Tool (milestones, gates, scope changes, statuses)
  - Finance systems (budgets, actuals, NPV)
  - HR/Resource systems (capabilities, utilization)
  - Risk/issue logs

## Development

```bash
# Format code
./run.sh format

# Run linters
./run.sh lint

# Check model health
./run.sh monitor
```

## Model Performance Targets

- Investment decision accuracy: +25%
- Risk detection lead time: -40%
- Portfolio throughput: +15%
- Value/cost ratio: +10-20%

## License

See PRD for project details and requirements.
