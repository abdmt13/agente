import json
from typing import Any, Optional
import structlog
from src.interfaces.ports.cache_service import ICacheService

logger = structlog.get_logger()


class RedisCacheAdapter(ICacheService):
    def __init__(self, host: str, port: int, password: Optional[str] = None, db: int = 0, enabled: bool = True):
        self._enabled = enabled
        self._in_memory_store: dict[str, Any] = {}
        self._client = None

        if self._enabled:
            try:
                import redis.asyncio as aioredis
                self._client = aioredis.Redis(
                    host=host,
                    port=port,
                    password=password,
                    db=db,
                    decode_responses=True
                )
            except Exception as e:
                logger.warning("No se pudo inicializar cliente de Redis, usando memoria interna", error=str(e))
                self._enabled = False

    async def get(self, key: str) -> Optional[Any]:
        if self._enabled and self._client:
            try:
                val = await self._client.get(key)
                return json.loads(val) if val else None
            except Exception as e:
                logger.warning("Fallo al leer de Redis, consultando memoria", key=key, error=str(e))
        return self._in_memory_store.get(key)

    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        self._in_memory_store[key] = value
        if self._enabled and self._client:
            try:
                serialized = json.dumps(value, default=str)
                await self._client.set(key, serialized, ex=ttl_seconds)
            except Exception as e:
                logger.warning("Fallo al escribir en Redis, guardado en memoria", key=key, error=str(e))

    async def delete(self, key: str) -> None:
        # Eliminar clave exacta o por prefijo en almacén en memoria
        to_remove = [k for k in self._in_memory_store if k == key or k.startswith(f"{key}:")]
        for k in to_remove:
            self._in_memory_store.pop(k, None)

        if self._enabled and self._client:
            try:
                await self._client.delete(key)
            except Exception as e:
                logger.warning("Fallo al eliminar de Redis", key=key, error=str(e))

    async def close(self) -> None:
        if self._client:
            try:
                await self._client.aclose()
            except Exception:
                pass
