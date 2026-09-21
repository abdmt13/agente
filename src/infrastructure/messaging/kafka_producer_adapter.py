import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import structlog
from src.interfaces.ports.event_publisher import IEventPublisher

logger = structlog.get_logger()


class KafkaProducerAdapter(IEventPublisher):
    def __init__(self, bootstrap_servers: str, enabled: bool = False):
        self._bootstrap_servers = bootstrap_servers
        self._enabled = enabled
        self._producer = None

    async def start(self) -> None:
        if self._enabled:
            try:
                from aiokafka import AIOKafkaProducer
                self._producer = AIOKafkaProducer(
                    bootstrap_servers=self._bootstrap_servers,
                    value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8")
                )
                await self._producer.start()
                logger.info("AIOKafkaProducer iniciado con éxito", servers=self._bootstrap_servers)
            except Exception as e:
                logger.warning("No se pudo conectar a Kafka. Los eventos se registrarán en logs", error=str(e))
                self._producer = None
                self._enabled = False

    async def stop(self) -> None:
        if self._producer:
            try:
                await self._producer.stop()
            except Exception:
                pass

    async def publish(self, topic: str, event_type: str, data: Dict[str, Any]) -> None:
        payload = {
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data
        }
        if self._enabled and self._producer:
            try:
                await self._producer.send_and_wait(topic, payload)
                logger.info("Evento publicado en Kafka", topic=topic, event_type=event_type)
                return
            except Exception as e:
                logger.warning("Fallo al publicar en Kafka, registrando en log", topic=topic, error=str(e))

        # Fallback estructurado en logger
        logger.info("Evento despachado (Modo local/desarrollo)", topic=topic, payload=payload)
