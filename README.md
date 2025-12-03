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

## 🌐 API

**FastAPI Endpoints:**

```python
POST /predict/risk          # Risk predictions
POST /predict/cost          # Cost overrun forecasts
POST /predict/success       # Success probability
POST /optimize/portfolio    # Portfolio optimization
GET  /models/{name}/info    # Model information
GET  /health                # Health check
```

**Interactive Docs**: http://localhost:8000/docs

## 🎨 Dashboard

**Streamlit App:**
```bash
streamlit run enhancements/dashboard_app.py
```

**Features:**
- 📊 Real-time predictions
- 📈 Portfolio visualizations
- 🎯 Risk matrices
- 📉 Pareto frontiers
- 🔍 SHAP explanations

## 🛠️ Technology Stack

<div align="center">

| Category | Technologies |
|----------|-------------|
| **ML/AI** | scikit-learn • XGBoost • LightGBM • TensorFlow • SHAP |
| **MLOps** | MLflow • Optuna • DVC |
| **API** | FastAPI • Pydantic • Uvicorn |
| **Data** | pandas • NumPy • SQLAlchemy |
| **Viz** | Plotly • Streamlit • Matplotlib |
| **DevOps** | Docker • GitHub Actions • pytest |

</div>

## 📊 Model Performance Targets

<div align="center">

```
┌─────────────────────────────────────────────┐
│  📈 Investment Accuracy      ▲ 25%         │
│  ⚡ Risk Detection Time      ▼ 40%         │
│  📊 Portfolio Throughput     ▲ 15%         │
│  💎 Value/Cost Ratio         ▲ 10-20%      │
└─────────────────────────────────────────────┘
```

</div>

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines.

## 📄 License

MIT License - See PRD for project details and requirements.

## 🙏 Acknowledgments

- Built with modern MLOps best practices
- Follows PMI standards for PPM
- Designed for production deployment

---

<div align="center">

**⭐ Star this repo if you find it useful!**

[Report Bug](https://github.com/migdam/Project_Portfolio/issues) • [Request Feature](https://github.com/migdam/Project_Portfolio/issues)

</div>
