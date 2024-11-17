# scheduler_center/monitoring/alerts.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import smtplib
from email.mime.text import MIMEText
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class AlertLevel:
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Alert:
    def __init__(self, level: str, message: str, details: Dict[str, Any]):
        self.level = level
        self.message = message
        self.details = details
        self.timestamp = datetime.now()

    def to_dict(self) -> dict:
        return {
            "level": self.level,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }


class AlertChannel(ABC):
    @abstractmethod
    def send_alert(self, alert: Alert) -> bool:
        pass


class EmailAlertChannel(AlertChannel):
    def __init__(self, smtp_config: dict):
        self.smtp_config = smtp_config

    def send_alert(self, alert: Alert) -> bool:
        try:
            msg = MIMEText(
                f"Alert Level: {alert.level}\n"
                f"Message: {alert.message}\n"
                f"Details: {alert.details}\n"
                f"Time: {alert.timestamp}"
            )
            msg['Subject'] = f"Scheduler Alert: {alert.level}"
            msg['From'] = self.smtp_config['from_email']
            msg['To'] = self.smtp_config['to_email']

            with smtplib.SMTP(self.smtp_config['host'], self.smtp_config['port']) as server:
                if self.smtp_config.get('use_tls', True):
                    server.starttls()
                server.login(
                    self.smtp_config['username'],
                    self.smtp_config['password']
                )
                server.send_message(msg)
            return True
        except Exception as e:
            logger.error(f"Failed to send email alert: {str(e)}")
            return False


class WebhookAlertChannel(AlertChannel):
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def send_alert(self, alert: Alert) -> bool:
        try:
            response = requests.post(
                self.webhook_url,
                json=alert.to_dict(),
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {str(e)}")
            return False


class AlertManager:
    def __init__(self):
        self.channels: List[AlertChannel] = []
        self.alert_history: List[Alert] = []

    def add_channel(self, channel: AlertChannel):
        self.channels.append(channel)

    def send_alert(self, alert: Alert) -> bool:
        self.alert_history.append(alert)
        success = True

        for channel in self.channels:
            if not channel.send_alert(alert):
                success = False
                logger.error(f"Failed to send alert through channel {channel.__class__.__name__}")

        return success

    def get_alert_history(self, limit: int = 100) -> List[Alert]:
        return sorted(
            self.alert_history,
            key=lambda x: x.timestamp,
            reverse=True
        )[:limit]
