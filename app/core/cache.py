"""
Cache simple en memoria para Amura API
"""
from datetime import datetime, timezone, timedelta
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)


class InMemoryCache:
    """Cache en memoria con TTL (Time To Live)"""

    def __init__(self):
        self._cache: dict = {}
        self._expiry: dict = {}

    def get(self, key: str) -> Optional[Any]:
        """Obtener valor del cache"""
        if key in self._cache:
            # Verificar expiración
            if key in self._expiry and datetime.now(timezone.utc) > self._expiry[key]:
                self.delete(key)
                return None
            return self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        """Guardar valor en cache con TTL (default: 5 minutos)"""
        self._cache[key] = value
        self._expiry[key] = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)

    def delete(self, key: str) -> None:
        """Eliminar valor del cache"""
        self._cache.pop(key, None)
        self._expiry.pop(key, None)

    def clear(self) -> None:
        """Limpiar todo el cache"""
        self._cache.clear()
        self._expiry.clear()

    def exists(self, key: str) -> bool:
        """Verificar si una key existe y no ha expirado"""
        return self.get(key) is not None


# Instancia global
cache = InMemoryCache()