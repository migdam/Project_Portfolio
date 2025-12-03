"""
Advanced Alerting System
Comprehensive alerts with PagerDuty, webhooks, and escalation
"""
from typing import Dict, List, Optional
from enum import Enum
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertChannel(Enum):
    """Alert delivery channels"""
    EMAIL = "email"
    SLACK = "slack"
    PAGERDUTY = "pagerduty"
    WEBHOOK = "webhook"


class AlertManager:
    """Manages alert routing and escalation"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.alert_history: List[Dict] = []
    
    def send_alert(
        self,
        title: str,
        message: str,
        severity: AlertSeverity,
        channels: List[AlertChannel],
        metadata: Dict = None
    ):
        """Send alert through specified channels"""
        
        alert = {
            "title": title,
            "message": message,
            "severity": severity.value,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        self.alert_history.append(alert)
        
        for channel in channels:
            try:
                if channel == AlertChannel.SLACK:
                    self._send_slack(alert)
                elif channel == AlertChannel.PAGERDUTY:
                    self._send_pagerduty(alert)
                elif channel == AlertChannel.WEBHOOK:
                    self._send_webhook(alert)
                elif channel == AlertChannel.EMAIL:
                    self._send_email(alert)
            except Exception as e:
                logger.error(f"Failed to send alert via {channel.value}: {e}")
    
    def _send_slack(self, alert: Dict):
        """Send to Slack"""
        webhook_url = self.config.get("slack_webhook_url")
        if not webhook_url:
            return
        
        color = {"info": "#36a64f", "warning": "#ff9900", "critical": "#ff0000"}
        
        payload = {
            "attachments": [{
                "color": color.get(alert["severity"], "#808080"),
                "title": alert["title"],
                "text": alert["message"],
                "footer": f"Portfolio ML | {alert['timestamp']}"
            }]
        }
        
        requests.post(webhook_url, json=payload)
    
    def _send_pagerduty(self, alert: Dict):
        """Send to PagerDuty"""
        api_key = self.config.get("pagerduty_api_key")
        if not api_key:
            return
        
        payload = {
            "routing_key": self.config["pagerduty_routing_key"],
            "event_action": "trigger",
            "payload": {
                "summary": alert["title"],
                "severity": alert["severity"],
                "source": "portfolio-ml",
                "custom_details": alert["metadata"]
            }
        }
        
        requests.post(
            "https://events.pagerduty.com/v2/enqueue",
            json=payload,
            headers={"Authorization": f"Token token={api_key}"}
        )
    
    def _send_webhook(self, alert: Dict):
        """Send to custom webhook"""
        webhook_url = self.config.get("custom_webhook_url")
        if not webhook_url:
            return
        requests.post(webhook_url, json=alert)
    
    def _send_email(self, alert: Dict):
        """Send email alert"""
        # Implementation depends on email service
        logger.info(f"Would send email: {alert['title']}")


# Escalation policies
class EscalationPolicy:
    """Define escalation rules for alerts"""
    
    def __init__(self):
        self.policies = {
            "critical": {
                "immediate": [AlertChannel.PAGERDUTY, AlertChannel.SLACK],
                "5_minutes": [AlertChannel.EMAIL],
                "escalate_after": 15  # minutes
            },
            "warning": {
                "immediate": [AlertChannel.SLACK],
                "30_minutes": [AlertChannel.EMAIL]
            }
        }
