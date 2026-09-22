from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError
from src.infrastructure.ioc.container import Container
from src.infrastructure.logging.logger import setup_logging
from src.infrastructure.monitoring.prometheus import metrics_endpoint
from src.presentation.middlewares.logging_middleware import StructlogLoggingMiddleware
from src.presentation.api.v1.router import api_v1_router, api_legacy_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Setup Logging
    logger = setup_logging(
        log_level=app.state.container.settings().LOG_LEVEL,
        app_env=app.state.container.settings().APP_ENV
    )
    logger.info("Iniciando backend FastAPI con Clean Architecture y CQRS...")

    # 2. Inicializar base de datos y crear tablas si no existen
    db_manager = app.state.container.db_manager()
    try:
        await db_manager.create_tables()
        logger.info("Base de datos y esquemas verificados con éxito.")
    except Exception as e:
        logger.warning("No se pudo conectar a la base de datos principal al arrancar.", error=str(e))

    # 3. Iniciar publicador de Kafka si está habilitado
    event_pub = app.state.container.event_publisher()
    await event_pub.start()

    yield

    # 4. Shutdown
    logger.info("Cerrando recursos del backend...")
    await event_pub.stop()
    cache_srv = app.state.container.cache_service()
    await cache_srv.close()
    await db_manager.close()
    logger.info("Backend detenido de forma segura.")


def create_app() -> FastAPI:
    container = Container()
    
    app = FastAPI(
        title="Chatbot IA - Backend Clean Architecture",
        description="Backend en Python 3.13 con FastAPI, SQLAlchemy 2.0 Async, Mediator CQRS, Redis, Kafka, JWT y Prometheus.",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc"
    )
    app.state.container = container

    @app.exception_handler(OperationalError)
    async def database_unavailable(request, exc):
        return JSONResponse(
            status_code=503,
            content={"detail": "No se pudo conectar a MySQL. Revisa DB_HOST, DB_USER y DB_PASSWORD en .env."},
        )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=container.settings().CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Middleware de Logging y Métricas
    app.add_middleware(StructlogLoggingMiddleware)

    # Métricas de Prometheus
    app.add_route("/metrics", metrics_endpoint)

    # Health Check
    @app.get("/health", tags=["Salud"])
    async def health_check():
        return {
            "status": "healthy",
            "app": container.settings().APP_NAME,
            "environment": container.settings().APP_ENV
        }

    # Routers API
    app.include_router(api_v1_router)
    app.include_router(api_legacy_router)

    # Servir archivos estáticos del frontend si existen en ./public
    public_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "public")
    if os.path.exists(public_dir):
        app.mount("/static", StaticFiles(directory=public_dir), name="static")

        @app.get("/", include_in_schema=False)
        async def serve_index():
            index_path = os.path.join(public_dir, "index.html")
            if os.path.exists(index_path):
                return FileResponse(index_path)
            return {"message": "Chatbot IA API en ejecución"}

        @app.get("/personal", include_in_schema=False)
        async def serve_staff():
            return FileResponse(os.path.join(public_dir, "personal.html"))

        @app.get("/{asset_name}", include_in_schema=False)
        async def serve_public_asset(asset_name: str):
            if asset_name not in {"app.js", "styles.css", "personal.js", "personal.css"}:
                from fastapi import HTTPException
                raise HTTPException(status_code=404)
            return FileResponse(os.path.join(public_dir, asset_name))

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.presentation.main:app", host="0.0.0.0", port=8000, reload=True)
