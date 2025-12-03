"""FastAPI server for model predictions."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import pandas as pd
import numpy as np
from pathlib import Path

from models import ProjectRiskModel, CostOverrunPredictor, SuccessLikelihoodModel, PortfolioOptimizer
from utils.config import load_config
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Load configuration
config = load_config()

# Initialize FastAPI app
app = FastAPI(
    title="Portfolio ML API",
    description="AI-Powered Project & Portfolio Machine Learning Models",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model cache
models_cache = {}


# Pydantic models for request/response
class ProjectFeatures(BaseModel):
    """Features for a single project."""
    scope_change_frequency: float
    milestone_variance: float
    team_experience_score: float
    dependency_count: int
    vendor_risk_score: float
    budget_utilization: float
    phase_duration: int


class RiskPredictionRequest(BaseModel):
    """Request for risk prediction."""
    projects: List[ProjectFeatures]


class RiskPredictionResponse(BaseModel):
    """Response for risk prediction."""
    predictions: List[Dict]


class CostPredictionRequest(BaseModel):
    """Request for cost overrun prediction."""
    projects: List[Dict]


class SuccessPredictionRequest(BaseModel):
    """Request for success prediction."""
    projects: List[Dict]


class PortfolioOptimizationRequest(BaseModel):
    """Request for portfolio optimization."""
    projects: List[Dict]
    budget_constraint: float
    resource_constraint: float


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    models_loaded: Dict[str, bool]
    version: str


def load_model(model_name: str):
    """Load model if not in cache."""
    if model_name not in models_cache:
        logger.info(f"Loading model: {model_name}")
        
        model_classes = {
            'prm': ProjectRiskModel,
            'cop': CostOverrunPredictor,
            'slm': SuccessLikelihoodModel,
            'po': PortfolioOptimizer
        }
        
        model = model_classes[model_name](config)
        
        # Try to load trained model
        try:
            model.load_model("models/artifacts")
            models_cache[model_name] = model
            logger.info(f"Model {model_name} loaded successfully")
        except FileNotFoundError:
            logger.warning(f"Trained model {model_name} not found")
            models_cache[model_name] = None
    
    return models_cache[model_name]


@app.get("/", response_model=Dict)
async def root():
    """Root endpoint."""
    return {
        "message": "Portfolio ML API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    models_loaded = {}
    
    for model_name in ['prm', 'cop', 'slm', 'po']:
        model = load_model(model_name)
        models_loaded[model_name] = model is not None and model.is_trained
    
    return HealthResponse(
        status="healthy",
        models_loaded=models_loaded,
        version="1.0.0"
    )


@app.post("/predict/risk", response_model=RiskPredictionResponse)
async def predict_risk(request: RiskPredictionRequest):
    """Predict project risk levels."""
    model = load_model('prm')
    
    if model is None or not model.is_trained:
        raise HTTPException(status_code=503, detail="Model not available")
    
    # Convert to DataFrame
    df = pd.DataFrame([p.dict() for p in request.projects])
    
    # Make predictions
    predictions, confidences = model.predict_with_confidence(df)
    risk_scores = model.get_risk_score(df)
    
    results = []
    for idx, (pred, conf, score) in enumerate(zip(predictions, confidences, risk_scores)):
        results.append({
            "project_index": idx,
            "risk_level": str(pred),
            "risk_score": float(score),
            "confidence": float(conf)
        })
    
    return RiskPredictionResponse(predictions=results)


@app.post("/predict/cost")
async def predict_cost_overrun(request: CostPredictionRequest):
    """Predict cost overruns."""
    model = load_model('cop')
    
    if model is None or not model.is_trained:
        raise HTTPException(status_code=503, detail="Model not available")
    
    df = pd.DataFrame(request.projects)
    
    predictions, confidences = model.predict_with_confidence(df)
    probabilities = model.predict_overrun_probability(df)
    
    results = []
    for idx, (pred, conf, prob) in enumerate(zip(predictions, confidences, probabilities)):
        results.append({
            "project_index": idx,
            "overrun_percentage": float(pred),
            "overrun_probability": float(prob),
            "confidence": float(conf)
        })
    
    return {"predictions": results}


@app.post("/predict/success")
async def predict_success(request: SuccessPredictionRequest):
    """Predict project success probability."""
    model = load_model('slm')
    
    if model is None or not model.is_trained:
        raise HTTPException(status_code=503, detail="Model not available")
    
    df = pd.DataFrame(request.projects)
    
    predictions, probabilities = model.predict_with_confidence(df)
    
    results = []
    for idx, (pred, prob) in enumerate(zip(predictions, probabilities)):
        results.append({
            "project_index": idx,
            "will_succeed": bool(pred),
            "success_probability": float(prob)
        })
    
    return {"predictions": results}


@app.post("/optimize/portfolio")
async def optimize_portfolio(request: PortfolioOptimizationRequest):
    """Optimize portfolio selection."""
    model = load_model('po')
    
    if model is None:
        raise HTTPException(status_code=503, detail="Optimizer not available")
    
    df = pd.DataFrame(request.projects)
    
    result = model.optimize(
        df,
        budget_constraint=request.budget_constraint,
        resource_constraint=request.resource_constraint
    )
    
    return result


@app.get("/models/{model_name}/info")
async def get_model_info(model_name: str):
    """Get model information."""
    if model_name not in ['prm', 'cop', 'slm', 'po']:
        raise HTTPException(status_code=404, detail="Model not found")
    
    model = load_model(model_name)
    
    if model is None:
        raise HTTPException(status_code=503, detail="Model not available")
    
    return {
        "model_name": model.model_name,
        "is_trained": model.is_trained,
        "features": model.feature_names,
        "model_type": model.model_config.get("type")
    }


def main():
    """Run the API server."""
    import uvicorn
    
    uvicorn.run(
        "api.server:app",
        host=config["api"]["host"],
        port=config["api"]["port"],
        reload=config["api"]["reload"]
    )


if __name__ == "__main__":
    main()
