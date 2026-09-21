import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import structlog
from src.infrastructure.monitoring.prometheus import REQUEST_COUNT, REQUEST_LATENCY

logger = structlog.get_logger()


class StructlogLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            path=request.url.path,
            method=request.method,
            client_ip=request.client.host if request.client else None
        )

        start_time = time.perf_counter()
        try:
            response = await call_next(request)
            duration = time.perf_counter() - start_time

            # Métricas Prometheus
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status_code=response.status_code
            ).inc()

            REQUEST_LATENCY.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(duration)

            logger.info(
                "HTTP Request completado",
                status_code=response.status_code,
                duration_ms=round(duration * 1000, 2)
            )
            response.headers["X-Request-ID"] = request_id
            return response

        except Exception as exc:
            duration = time.perf_counter() - start_time
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status_code=500
            ).inc()

            logger.error(
                "HTTP Request fallido",
                error=str(exc),
                duration_ms=round(duration * 1000, 2)
            )
            raise exc
