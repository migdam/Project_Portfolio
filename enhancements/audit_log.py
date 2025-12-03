"""Audit logging for model predictions."""

from datetime import datetime
from pathlib import Path
import json
import hashlib

from utils.logger import setup_logger

logger = setup_logger(__name__)


class AuditLogger:
    """Log all predictions for compliance and auditing."""
    
    def __init__(self, log_dir: str = "logs/audit"):
        """Initialize audit logger."""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.current_log_file = self.log_dir / f"audit_{datetime.now().strftime('%Y%m%d')}.jsonl"
    
    def log_prediction(
        self,
        model_name: str,
        input_data: dict,
        prediction: dict,
        user_id: str = None,
        session_id: str = None
    ):
        """
        Log a single prediction.
        
        Args:
            model_name: Name of model used
            input_data: Input features
            prediction: Model prediction
            user_id: Optional user identifier
            session_id: Optional session identifier
        """
        # Create audit record
        record = {
            "timestamp": datetime.now().isoformat(),
            "model_name": model_name,
            "prediction_id": self._generate_prediction_id(input_data, prediction),
            "input_hash": self._hash_data(input_data),
            "prediction": prediction,
            "user_id": user_id,
            "session_id": session_id,
            "model_version": "1.0.0"  # TODO: Get from model metadata
        }
        
        # Append to log file
        with open(self.current_log_file, 'a') as f:
            f.write(json.dumps(record) + '\n')
        
        logger.debug(f"Logged prediction: {record['prediction_id']}")
    
    def _generate_prediction_id(self, input_data: dict, prediction: dict) -> str:
        """Generate unique prediction ID."""
        combined = f"{datetime.now().isoformat()}_{json.dumps(input_data)}_{json.dumps(prediction)}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    def _hash_data(self, data: dict) -> str:
        """Hash input data for privacy."""
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
    
    def get_predictions_by_date(self, date: str) -> list:
        """Retrieve predictions for a specific date."""
        log_file = self.log_dir / f"audit_{date}.jsonl"
        
        if not log_file.exists():
            return []
        
        predictions = []
        with open(log_file, 'r') as f:
            for line in f:
                predictions.append(json.loads(line))
        
        return predictions
