"""Demo FastAPI server for screenshots"""
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
import random

app = FastAPI(
    title="Portfolio ML API",
    description="AI-Powered Project & Portfolio Machine Learning",
    version="1.0.0"
)

class ProjectInput(BaseModel):
    project_id: str
    budget: float
    duration_months: int
    team_size: int
    complexity_score: float
    scope_changes: int

class RiskPrediction(BaseModel):
    project_id: str
    risk_level: str
    risk_score: int
    confidence: float
    top_factors: List[Dict[str, float]]

class CostPrediction(BaseModel):
    project_id: str
    predicted_overrun_pct: float
    predicted_final_cost: float
    confidence: float

class SuccessPrediction(BaseModel):
    project_id: str
    success_probability: float
    confidence: float
    key_factors: List[str]

@app.get("/")
def root():
    return {
        "service": "Portfolio ML API",
        "version": "1.0.0",
        "models": ["PRM", "COP", "SLM", "PO"],
        "status": "operational"
    }

@app.post("/predict/risk", response_model=RiskPrediction)
def predict_risk(project: ProjectInput):
    """Predict project risk using PRM model"""
    risk_score = min(100, int(project.scope_changes * 15 + project.complexity_score * 10))
    risk_level = "HIGH" if risk_score > 70 else "MEDIUM" if risk_score > 40 else "LOW"
    
    return RiskPrediction(
        project_id=project.project_id,
        risk_level=risk_level,
        risk_score=risk_score,
        confidence=0.89,
        top_factors=[
            {"feature": "scope_change_frequency", "impact": 0.32, "value": project.scope_changes},
            {"feature": "complexity_score", "impact": 0.28, "value": project.complexity_score},
            {"feature": "team_experience", "impact": -0.15, "value": project.team_size}
        ]
    )

@app.post("/predict/cost", response_model=CostPrediction)
def predict_cost_overrun(project: ProjectInput):
    """Predict cost overrun using COP model"""
    overrun_pct = (project.scope_changes * 3.5 + project.complexity_score * 2)
    
    return CostPrediction(
        project_id=project.project_id,
        predicted_overrun_pct=round(overrun_pct, 2),
        predicted_final_cost=round(project.budget * (1 + overrun_pct/100), 2),
        confidence=0.84
    )

@app.post("/predict/success", response_model=SuccessPrediction)
def predict_success(project: ProjectInput):
    """Predict project success using SLM model"""
    success_prob = max(0, min(1, 0.95 - (project.scope_changes * 0.05) - (project.complexity_score * 0.02)))
    
    return SuccessPrediction(
        project_id=project.project_id,
        success_probability=round(success_prob, 3),
        confidence=0.91,
        key_factors=[
            "Team experience and capability",
            "Scope stability and governance",
            "Resource availability and planning"
        ]
    )

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "models": {
            "PRM": {"status": "active", "accuracy": 0.89, "last_trained": "2025-11-28"},
            "COP": {"status": "active", "r2_score": 0.82, "last_trained": "2025-11-27"},
            "SLM": {"status": "active", "auc_roc": 0.91, "last_trained": "2025-11-29"},
            "PO": {"status": "active", "optimization_time": "2.3s", "last_trained": "2025-11-26"}
        },
        "drift_status": "no_drift_detected"
    }

@app.get("/models")
def list_models():
    return {
        "models": [
            {
                "id": "PRM",
                "name": "Project Risk Model",
                "description": "Predicts schedule slippage, budget overruns, and resource bottlenecks",
                "endpoint": "/predict/risk"
            },
            {
                "id": "COP",
                "name": "Cost Overrun Predictor",
                "description": "Forecasts probability and magnitude of cost overruns",
                "endpoint": "/predict/cost"
            },
            {
                "id": "SLM",
                "name": "Success Likelihood Model",
                "description": "Estimates project success probability based on historical patterns",
                "endpoint": "/predict/success"
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
