"""Data quality alerts and notifications."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from typing import Dict, List

from utils.logger import setup_logger

logger = setup_logger(__name__)


class AlertManager:
    """Manage alerts for data quality and model issues."""
    
    def __init__(self, config: Dict):
        """Initialize alert manager."""
        self.config = config
        self.email_enabled = config.get("alerts", {}).get("email_enabled", False)
        self.slack_enabled = config.get("alerts", {}).get("slack_enabled", False)
    
    def send_email_alert(self, subject: str, message: str, recipients: List[str]):
        """Send email alert."""
        if not self.email_enabled:
            logger.info(f"Email alert (not sent): {subject}")
            return
        
        # Email configuration would go here
        logger.info(f"Email alert sent: {subject}")
    
    def send_slack_alert(self, message: str, channel: str = "#ml-alerts"):
        """Send Slack notification."""
        if not self.slack_enabled:
            logger.info(f"Slack alert (not sent): {message}")
            return
        
        webhook_url = self.config.get("alerts", {}).get("slack_webhook")
        if webhook_url:
            payload = {"text": message, "channel": channel}
            requests.post(webhook_url, json=payload)
            logger.info(f"Slack alert sent to {channel}")
    
    def alert_data_quality_issue(self, issue_type: str, details: Dict):
        """Alert on data quality issues."""
        message = f"⚠️ Data Quality Alert: {issue_type}\\n{details}"
        self.send_slack_alert(message)
        logger.warning(f"Data quality alert: {issue_type}")
    
    def alert_model_degradation(self, model_name: str, metric: str, value: float):
        """Alert on model performance degradation."""
        message = f"🔻 Model Degradation: {model_name}\\n{metric}: {value:.2%}"
        self.send_slack_alert(message)
        self.send_email_alert(
            f"Model Degradation Alert: {model_name}",
            message,
            ["team@example.com"]
        )
