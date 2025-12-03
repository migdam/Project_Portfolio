"""
Model Feedback Loop
Capture user feedback on predictions for continuous improvement
"""
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import json
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class FeedbackCollector:
    """Collects and stores user feedback on model predictions"""
    
    def __init__(self, storage_path: str = "data/feedback"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def record_feedback(
        self,
        prediction_id: str,
        model_name: str,
        project_id: str,
        predicted_value: float,
        actual_value: Optional[float] = None,
        user_rating: Optional[int] = None,  # 1-5 stars
        user_comment: Optional[str] = None,
        correction: Optional[Dict] = None,
        feedback_type: str = "rating",  # rating, correction, validation
        user_id: str = None
    ) -> Dict:
        """Record user feedback on a prediction"""
        
        feedback_entry = {
            "feedback_id": f"fb_{datetime.utcnow().timestamp()}",
            "prediction_id": prediction_id,
            "model_name": model_name,
            "project_id": project_id,
            "predicted_value": predicted_value,
            "actual_value": actual_value,
            "user_rating": user_rating,
            "user_comment": user_comment,
            "correction": correction,
            "feedback_type": feedback_type,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "processed": False
        }
        
        # Save to daily file
        date_str = datetime.utcnow().strftime("%Y%m%d")
        feedback_file = self.storage_path / f"feedback_{date_str}.jsonl"
        
        with open(feedback_file, 'a') as f:
            f.write(json.dumps(feedback_entry) + '\n')
        
        logger.info(f"Recorded feedback for prediction {prediction_id}")
        return feedback_entry
    
    def get_feedback(
        self,
        model_name: str = None,
        start_date: datetime = None,
        end_date: datetime = None,
        feedback_type: str = None
    ) -> List[Dict]:
        """Retrieve feedback records"""
        
        feedback_records = []
        
        # Scan feedback files
        for feedback_file in sorted(self.storage_path.glob("feedback_*.jsonl")):
            with open(feedback_file, 'r') as f:
                for line in f:
                    record = json.loads(line)
                    
                    # Apply filters
                    if model_name and record["model_name"] != model_name:
                        continue
                    
                    record_time = datetime.fromisoformat(record["timestamp"])
                    if start_date and record_time < start_date:
                        continue
                    if end_date and record_time > end_date:
                        continue
                    
                    if feedback_type and record["feedback_type"] != feedback_type:
                        continue
                    
                    feedback_records.append(record)
        
        return feedback_records
    
    def aggregate_feedback_metrics(self, model_name: str) -> Dict:
        """Aggregate feedback metrics for a model"""
        
        feedback = self.get_feedback(model_name=model_name)
        
        if not feedback:
            return {
                "model_name": model_name,
                "total_feedback": 0,
                "avg_rating": None,
                "feedback_by_type": {}
            }
        
        ratings = [f["user_rating"] for f in feedback if f["user_rating"] is not None]
        
        feedback_by_type = {}
        for f in feedback:
            ftype = f["feedback_type"]
            if ftype not in feedback_by_type:
                feedback_by_type[ftype] = 0
            feedback_by_type[ftype] += 1
        
        return {
            "model_name": model_name,
            "total_feedback": len(feedback),
            "avg_rating": sum(ratings) / len(ratings) if ratings else None,
            "feedback_by_type": feedback_by_type,
            "last_feedback": feedback[-1]["timestamp"] if feedback else None
        }


class FeedbackAnalyzer:
    """Analyzes feedback to identify model improvement opportunities"""
    
    def __init__(self, feedback_collector: FeedbackCollector):
        self.collector = feedback_collector
    
    def identify_prediction_errors(
        self,
        model_name: str,
        threshold: float = 0.2
    ) -> List[Dict]:
        """Identify predictions with significant errors"""
        
        feedback = self.collector.get_feedback(
            model_name=model_name,
            feedback_type="validation"
        )
        
        errors = []
        for f in feedback:
            if f["actual_value"] is None:
                continue
            
            predicted = f["predicted_value"]
            actual = f["actual_value"]
            
            # Calculate relative error
            rel_error = abs(predicted - actual) / (abs(actual) + 1e-8)
            
            if rel_error > threshold:
                errors.append({
                    "project_id": f["project_id"],
                    "prediction_id": f["prediction_id"],
                    "predicted_value": predicted,
                    "actual_value": actual,
                    "relative_error": rel_error,
                    "timestamp": f["timestamp"]
                })
        
        return sorted(errors, key=lambda x: x["relative_error"], reverse=True)
    
    def find_systematic_biases(self, model_name: str) -> Dict:
        """Detect systematic biases in predictions"""
        
        feedback = self.collector.get_feedback(
            model_name=model_name,
            feedback_type="validation"
        )
        
        predictions = []
        actuals = []
        
        for f in feedback:
            if f["actual_value"] is not None:
                predictions.append(f["predicted_value"])
                actuals.append(f["actual_value"])
        
        if not predictions:
            return {"bias_detected": False}
        
        predictions = pd.Series(predictions)
        actuals = pd.Series(actuals)
        
        # Calculate bias metrics
        mean_error = (predictions - actuals).mean()
        overestimation_rate = (predictions > actuals).sum() / len(predictions)
        
        return {
            "bias_detected": abs(mean_error) > 0.1,
            "mean_error": float(mean_error),
            "overestimation_rate": float(overestimation_rate),
            "underestimation_rate": 1.0 - float(overestimation_rate),
            "sample_size": len(predictions)
        }
    
    def generate_retraining_dataset(
        self,
        model_name: str,
        min_feedback_count: int = 50
    ) -> Optional[pd.DataFrame]:
        """Generate dataset from feedback for model retraining"""
        
        feedback = self.collector.get_feedback(
            model_name=model_name,
            feedback_type="validation"
        )
        
        # Filter feedback with actual values
        valid_feedback = [f for f in feedback if f["actual_value"] is not None]
        
        if len(valid_feedback) < min_feedback_count:
            logger.warning(f"Insufficient feedback for retraining: {len(valid_feedback)}/{min_feedback_count}")
            return None
        
        # Convert to DataFrame
        retraining_data = pd.DataFrame([
            {
                "project_id": f["project_id"],
                "predicted_value": f["predicted_value"],
                "actual_value": f["actual_value"],
                "timestamp": f["timestamp"]
            }
            for f in valid_feedback
        ])
        
        logger.info(f"Generated retraining dataset with {len(retraining_data)} samples")
        return retraining_data
    
    def recommend_model_improvements(self, model_name: str) -> List[str]:
        """Recommend improvements based on feedback analysis"""
        
        recommendations = []
        
        # Check for systematic bias
        bias_analysis = self.find_systematic_biases(model_name)
        if bias_analysis["bias_detected"]:
            if bias_analysis["overestimation_rate"] > 0.7:
                recommendations.append(
                    "Model consistently overestimates - consider recalibrating thresholds or adding penalty terms"
                )
            elif bias_analysis["overestimation_rate"] < 0.3:
                recommendations.append(
                    "Model consistently underestimates - review feature engineering and training data balance"
                )
        
        # Check for high error rate
        errors = self.identify_prediction_errors(model_name, threshold=0.2)
        if len(errors) > 10:
            recommendations.append(
                f"High number of prediction errors detected ({len(errors)}) - investigate data quality and feature relevance"
            )
        
        # Check feedback metrics
        metrics = self.collector.aggregate_feedback_metrics(model_name)
        if metrics["avg_rating"] and metrics["avg_rating"] < 3.0:
            recommendations.append(
                f"Low user satisfaction (avg rating: {metrics['avg_rating']:.1f}) - gather qualitative feedback and review UX"
            )
        
        # Check for sufficient retraining data
        retraining_data = self.generate_retraining_dataset(model_name)
        if retraining_data is not None and len(retraining_data) >= 100:
            recommendations.append(
                f"Sufficient feedback collected ({len(retraining_data)} samples) - schedule model retraining"
            )
        
        return recommendations if recommendations else ["No immediate improvements needed based on current feedback"]


class ActiveLearningSelector:
    """Select predictions that would benefit most from user feedback"""
    
    def __init__(self, feedback_collector: FeedbackCollector):
        self.collector = feedback_collector
    
    def select_for_feedback(
        self,
        predictions: List[Dict],
        strategy: str = "uncertainty",
        count: int = 10
    ) -> List[str]:
        """Select predictions to request feedback on"""
        
        if strategy == "uncertainty":
            # Select predictions with highest uncertainty (closest to decision boundary)
            sorted_preds = sorted(
                predictions,
                key=lambda p: abs(p.get("confidence", 0.5) - 0.5),
                reverse=False
            )
        
        elif strategy == "high_impact":
            # Select high-value projects
            sorted_preds = sorted(
                predictions,
                key=lambda p: p.get("project_value", 0),
                reverse=True
            )
        
        elif strategy == "random":
            # Random sampling
            import random
            sorted_preds = random.sample(predictions, min(count, len(predictions)))
        
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
        
        return [p["prediction_id"] for p in sorted_preds[:count]]
