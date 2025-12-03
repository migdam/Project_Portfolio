"""Batch prediction pipeline for scheduled inference."""

from pathlib import Path
from datetime import datetime
import pandas as pd
import json

from models import ProjectRiskModel, CostOverrunPredictor, SuccessLikelihoodModel
from utils.logger import setup_logger
from utils.config import load_config

logger = setup_logger(__name__)


class BatchPredictor:
    """Run batch predictions on portfolio."""
    
    def __init__(self, config: dict):
        """Initialize batch predictor."""
        self.config = config
        self.output_dir = Path("predictions")
        self.output_dir.mkdir(exist_ok=True)
    
    def predict_all_models(self, data_path: str) -> dict:
        """
        Run predictions with all models.
        
        Args:
            data_path: Path to input data CSV
            
        Returns:
            Dictionary with all predictions
        """
        logger.info(f"Running batch predictions on {data_path}")
        
        df = pd.read_csv(data_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "input_file": data_path,
            "n_projects": len(df),
            "predictions": {}
        }
        
        # PRM predictions
        try:
            prm = ProjectRiskModel(self.config)
            prm.load_model("models/artifacts")
            
            predictions, confidences = prm.predict_with_confidence(df)
            risk_scores = prm.get_risk_score(df)
            
            results["predictions"]["risk"] = {
                "predictions": predictions.tolist(),
                "confidences": confidences.tolist(),
                "risk_scores": risk_scores.tolist()
            }
            logger.info("✓ Risk predictions complete")
        except Exception as e:
            logger.error(f"Risk prediction failed: {e}")
        
        # COP predictions
        try:
            cop = CostOverrunPredictor(self.config)
            cop.load_model("models/artifacts")
            
            predictions, confidences = cop.predict_with_confidence(df)
            probabilities = cop.predict_overrun_probability(df)
            
            results["predictions"]["cost"] = {
                "overrun_pct": predictions.tolist(),
                "confidences": confidences.tolist(),
                "probabilities": probabilities.tolist()
            }
            logger.info("✓ Cost predictions complete")
        except Exception as e:
            logger.error(f"Cost prediction failed: {e}")
        
        # SLM predictions
        try:
            slm = SuccessLikelihoodModel(self.config)
            slm.load_model("models/artifacts")
            
            predictions, probabilities = slm.predict_with_confidence(df)
            
            results["predictions"]["success"] = {
                "predictions": predictions.tolist(),
                "probabilities": probabilities.tolist()
            }
            logger.info("✓ Success predictions complete")
        except Exception as e:
            logger.error(f"Success prediction failed: {e}")
        
        # Save results
        output_file = self.output_dir / f"batch_predictions_{timestamp}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Batch predictions saved to {output_file}")
        return results
