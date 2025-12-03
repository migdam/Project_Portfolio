"""
WebSocket Notifications Service
Real-time alerts and prediction updates for dashboard clients
"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict, Set
import asyncio
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and broadcasts"""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.subscriptions: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str = None):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"Client {client_id} connected. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        self.active_connections.discard(websocket)
        # Remove from all subscriptions
        for channel in self.subscriptions.values():
            channel.discard(websocket)
    
    async def subscribe(self, websocket: WebSocket, channel: str):
        """Subscribe connection to a channel"""
        if channel not in self.subscriptions:
            self.subscriptions[channel] = set()
        self.subscriptions[channel].add(websocket)
    
    async def unsubscribe(self, websocket: WebSocket, channel: str):
        """Unsubscribe connection from a channel"""
        if channel in self.subscriptions:
            self.subscriptions[channel].discard(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific client"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        """Broadcast to all connected clients"""
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting: {e}")
                disconnected.add(connection)
        
        # Clean up failed connections
        for conn in disconnected:
            self.disconnect(conn)
    
    async def broadcast_to_channel(self, message: str, channel: str):
        """Broadcast to specific channel subscribers"""
        if channel not in self.subscriptions:
            return
        
        disconnected = set()
        for connection in self.subscriptions[channel]:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting to channel {channel}: {e}")
                disconnected.add(connection)
        
        # Clean up failed connections
        for conn in disconnected:
            self.disconnect(conn)


manager = ConnectionManager()


class NotificationService:
    """Service for sending typed notifications"""
    
    @staticmethod
    async def send_prediction_update(project_id: str, prediction_type: str, result: Dict):
        """Notify about new prediction"""
        message = {
            "type": "prediction_update",
            "timestamp": datetime.utcnow().isoformat(),
            "project_id": project_id,
            "prediction_type": prediction_type,
            "result": result
        }
        await manager.broadcast_to_channel(json.dumps(message), f"project_{project_id}")
        await manager.broadcast_to_channel(json.dumps(message), "predictions")
    
    @staticmethod
    async def send_risk_alert(project_id: str, risk_level: str, risk_score: int, message: str):
        """Send risk alert notification"""
        alert = {
            "type": "risk_alert",
            "timestamp": datetime.utcnow().isoformat(),
            "project_id": project_id,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "message": message,
            "severity": "critical" if risk_level == "HIGH" else "warning"
        }
        await manager.broadcast_to_channel(json.dumps(alert), "alerts")
        await manager.broadcast(json.dumps(alert))
    
    @staticmethod
    async def send_model_update(model_name: str, status: str, metrics: Dict):
        """Notify about model training/deployment updates"""
        message = {
            "type": "model_update",
            "timestamp": datetime.utcnow().isoformat(),
            "model_name": model_name,
            "status": status,
            "metrics": metrics
        }
        await manager.broadcast_to_channel(json.dumps(message), "model_updates")
    
    @staticmethod
    async def send_drift_alert(model_name: str, drift_score: float, features: List[str]):
        """Alert about detected data drift"""
        alert = {
            "type": "drift_alert",
            "timestamp": datetime.utcnow().isoformat(),
            "model_name": model_name,
            "drift_score": drift_score,
            "affected_features": features,
            "severity": "critical" if drift_score > 0.3 else "warning"
        }
        await manager.broadcast_to_channel(json.dumps(alert), "alerts")
        await manager.broadcast_to_channel(json.dumps(alert), "model_updates")
    
    @staticmethod
    async def send_portfolio_update(portfolio_id: str, metrics: Dict):
        """Send portfolio optimization updates"""
        message = {
            "type": "portfolio_update",
            "timestamp": datetime.utcnow().isoformat(),
            "portfolio_id": portfolio_id,
            "metrics": metrics
        }
        await manager.broadcast_to_channel(json.dumps(message), f"portfolio_{portfolio_id}")


# FastAPI WebSocket endpoint
async def websocket_endpoint(websocket: WebSocket, client_id: str = None):
    """Main WebSocket endpoint handler"""
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle subscription requests
            if message.get("action") == "subscribe":
                channel = message.get("channel")
                await manager.subscribe(websocket, channel)
                await manager.send_personal_message(
                    json.dumps({"status": "subscribed", "channel": channel}),
                    websocket
                )
            
            elif message.get("action") == "unsubscribe":
                channel = message.get("channel")
                await manager.unsubscribe(websocket, channel)
                await manager.send_personal_message(
                    json.dumps({"status": "unsubscribed", "channel": channel}),
                    websocket
                )
            
            elif message.get("action") == "ping":
                await manager.send_personal_message(
                    json.dumps({"type": "pong", "timestamp": datetime.utcnow().isoformat()}),
                    websocket
                )
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"Client {client_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


# Integration with FastAPI
def setup_websocket_routes(app):
    """Add WebSocket routes to FastAPI app"""
    
    @app.websocket("/ws/{client_id}")
    async def websocket_route(websocket: WebSocket, client_id: str):
        await websocket_endpoint(websocket, client_id)
    
    @app.websocket("/ws")
    async def websocket_route_anonymous(websocket: WebSocket):
        await websocket_endpoint(websocket)
