from typing import Optional
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.requests import Request
from starlette.responses import Response

# Contadores de peticiones y latencia
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total de peticiones HTTP procesadas",
    ["method", "endpoint", "status_code"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "Duración de peticiones HTTP en segundos",
    ["method", "endpoint"]
)

CHAT_MESSAGES_TOTAL = Counter(
    "chatbot_messages_total",
    "Total de mensajes procesados por el chatbot",
    ["role", "status"]
)

MEDIATOR_DISPATCH_COUNT = Counter(
    "mediator_dispatches_total",
    "Total de llamadas despachadas a través de Mediator",
    ["request_type", "handler"]
)


def metrics_endpoint(request: Optional[Request] = None) -> Response:
    """Endpoint para exponer métricas en formato Prometheus."""
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)

