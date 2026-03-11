"""
WebSocket Manager - Maneja conexiones en tiempo real
"""
from typing import Dict, List, Set
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Administra conexiones WebSocket activas"""

    def __init__(self):
        # user_id -> lista de conexiones (un usuario puede tener varias pestañas)
        self._active_connections: Dict[str, List[WebSocket]] = {}
        # Canales de suscripción: channel_name -> set de user_ids
        self._channels: Dict[str, Set[str]] = {}

    async def connect(self, websocket: WebSocket, user_id: str) -> None:
        """Acepta una conexión WebSocket"""
        await websocket.accept()
        if user_id not in self._active_connections:
            self._active_connections[user_id] = []
        self._active_connections[user_id].append(websocket)
        logger.info(f"🔌 WebSocket connected: user={user_id} | Total connections: {self._total_connections()}")

    def disconnect(self, websocket: WebSocket, user_id: str) -> None:
        """Desconecta un WebSocket"""
        if user_id in self._active_connections:
            self._active_connections[user_id] = [
                ws for ws in self._active_connections[user_id] if ws != websocket
            ]
            if not self._active_connections[user_id]:
                del self._active_connections[user_id]
                # Remover de todos los canales
                for channel in list(self._channels.keys()):
                    self._channels[channel].discard(user_id)
                    if not self._channels[channel]:
                        del self._channels[channel]
        logger.info(f"🔌 WebSocket disconnected: user={user_id} | Total connections: {self._total_connections()}")

    def is_online(self, user_id: str) -> bool:
        """Verifica si un usuario está conectado"""
        return user_id in self._active_connections and len(self._active_connections[user_id]) > 0

    def get_online_users(self) -> List[str]:
        """Retorna lista de user_ids conectados"""
        return list(self._active_connections.keys())

    # ── Enviar mensajes ───────────────────────────────────────

    async def send_personal(self, user_id: str, message: dict) -> None:
        """Envía un mensaje a todas las conexiones de un usuario"""
        if user_id in self._active_connections:
            dead_connections = []
            for ws in self._active_connections[user_id]:
                try:
                    await ws.send_json(message)
                except Exception:
                    dead_connections.append(ws)
            # Limpiar conexiones muertas
            for ws in dead_connections:
                self._active_connections[user_id].remove(ws)

    async def broadcast(self, message: dict, exclude_user: str = None) -> None:
        """Envía un mensaje a TODOS los usuarios conectados"""
        for user_id in list(self._active_connections.keys()):
            if user_id != exclude_user:
                await self.send_personal(user_id, message)

    async def send_to_channel(self, channel: str, message: dict, exclude_user: str = None) -> None:
        """Envía un mensaje a todos los suscriptores de un canal"""
        if channel in self._channels:
            for user_id in self._channels[channel]:
                if user_id != exclude_user:
                    await self.send_personal(user_id, message)

    # ── Canales / Suscripciones ───────────────────────────────

    def subscribe(self, user_id: str, channel: str) -> None:
        """Suscribe un usuario a un canal"""
        if channel not in self._channels:
            self._channels[channel] = set()
        self._channels[channel].add(user_id)
        logger.info(f"📡 User {user_id} subscribed to channel: {channel}")

    def unsubscribe(self, user_id: str, channel: str) -> None:
        """Desuscribe un usuario de un canal"""
        if channel in self._channels:
            self._channels[channel].discard(user_id)
            if not self._channels[channel]:
                del self._channels[channel]

    # ── Helpers ───────────────────────────────────────────────

    def _total_connections(self) -> int:
        return sum(len(conns) for conns in self._active_connections.values())


# Instancia global
manager = ConnectionManager()