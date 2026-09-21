from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # App Settings
    APP_NAME: str = "Chatbot IA Backend"
    APP_ENV: str = "development"
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Database Settings (MySQL / Async)
    DB_HOST: str = "127.0.0.2"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "agentevirtualmvp"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_ECHO: bool = False
    # Alternativa directa para SQLAlchemy URL (ej. sqlite+aiosqlite:///./test.db o mysql+asyncmy://...)
    DATABASE_URL: Optional[str] = None

    @property
    def async_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        # Por defecto usar asyncmy para MySQL
        user = self.DB_USER
        pwd = f":{self.DB_PASSWORD}" if self.DB_PASSWORD else ""
        return f"mysql+asyncmy://{user}{pwd}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

    # JWT Security Settings
    JWT_SECRET_KEY: str = "super-secret-jwt-key-for-clean-architecture-change-in-prod"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # Redis Cache Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    REDIS_ENABLED: bool = False

    # Kafka Messaging Settings
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_ENABLED: bool = False
    KAFKA_TOPIC_CHAT_EVENTS: str = "chatbot-chat-events"
    KAFKA_TOPIC_AUTH_EVENTS: str = "chatbot-auth-events"

    # AI Provider Settings
    AI_PROVIDER: str = "gemini"  # 'gemini' | 'openai'
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_THINKING_LEVEL: str = "minimal"
    GEMINI_TIMEOUT_MS: int = 15000

    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Bot Instructions
    BOT_INSTRUCTIONS: str = (
        "Eres el asistente virtual de Mi Negocio. Responde en español, "
        "con amabilidad y claridad. No inventes precios, políticas ni datos. "
        "Si no tienes información suficiente, dilo y ofrece transferir la conversación a una persona."
    )

    # CORS
    CORS_ORIGINS: List[str] = ["*"]
