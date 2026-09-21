import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from src.presentation.main import create_app
from src.infrastructure.config.settings import Settings
from src.infrastructure.ioc.container import Container
from src.domain.entities.user import User
from src.domain.entities.conversation import Conversation
from src.application.commands.chat_commands import SendMessageCommand, RegisterUserCommand, AuthenticateUserCommand
from src.application.queries.chat_queries import GetConversationHistoryQuery, GetPropertiesCatalogQuery


@pytest.fixture
def test_settings():
    return Settings(
        DATABASE_URL="sqlite+aiosqlite:///:memory:",
        JWT_SECRET_KEY="test-secret-key-that-is-at-least-32-bytes-long",
        REDIS_ENABLED=False,
        KAFKA_ENABLED=False,
        AI_PROVIDER="mock"
    )



@pytest_asyncio.fixture
async def app_and_client(test_settings):
    app = create_app()
    # Override settings for in-memory testing
    app.state.container.settings.override(test_settings)
    
    # Initialize in-memory tables
    db_manager = app.state.container.db_manager()
    await db_manager.create_tables()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield app, client

    await db_manager.close()


@pytest.mark.asyncio
async def test_health_check(app_and_client):
    app, client = app_and_client
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_prometheus_metrics(app_and_client):
    app, client = app_and_client
    response = await client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text


@pytest.mark.asyncio
async def test_user_registration_and_login_flow(app_and_client):
    app, client = app_and_client
    # 1. Register
    reg_payload = {
        "email": "asesor@inmobiliaria.com",
        "password": "password123",
        "full_name": "Asesor Inmobiliario",
        "role": "agent"
    }
    reg_resp = await client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_resp.status_code == 201
    user_data = reg_resp.json()
    assert user_data["email"] == "asesor@inmobiliaria.com"
    assert user_data["role"] == "agent"

    # 2. Login
    login_payload = {
        "email": "asesor@inmobiliaria.com",
        "password": "password123"
    }
    login_resp = await client.post("/api/v1/auth/login", json=login_payload)
    assert login_resp.status_code == 200
    token_data = login_resp.json()
    assert "access_token" in token_data
    token = token_data["access_token"]

    # 3. Access Protected /auth/me
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = await client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["email"] == "asesor@inmobiliaria.com"
    assert me_data["role"] == "agent"


@pytest.mark.asyncio
async def test_chat_and_conversation_cqrs_flow(app_and_client):
    app, client = app_and_client
    session_id = "test-session-12345"

    # 1. Send chat message
    chat_payload = {
        "sessionId": session_id,
        "message": "Hola, ¿qué opciones tienen disponibles?"
    }
    chat_resp = await client.post("/api/chat", json=chat_payload)
    assert chat_resp.status_code == 200
    data = chat_resp.json()
    assert "reply" in data
    assert data["sessionId"] == session_id

    # 2. Get history
    history_resp = await client.get(f"/api/chat/{session_id}")
    assert history_resp.status_code == 200
    history_data = history_resp.json()
    assert history_data["sessionId"] == session_id
    assert len(history_data["messages"]) >= 2  # user + assistant

    # 3. Delete conversation
    del_resp = await client.delete(f"/api/chat/{session_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["ok"] is True

    # 4. Verify history is empty
    empty_history = await client.get(f"/api/chat/{session_id}")
    assert empty_history.status_code == 200
    assert len(empty_history.json()["messages"]) == 0


@pytest.mark.asyncio
async def test_mediator_direct_dispatch(app_and_client):
    app, _ = app_and_client
    mediator = app.state.container.mediator()

    # Dispatch Command directly via Mediator
    command = RegisterUserCommand(
        email="direct@mediator.com",
        password="securepassword",
        full_name="Mediator User",
        role="customer"
    )
    user_dto = await mediator.send(command)
    assert user_dto.email == "direct@mediator.com"

    # Dispatch Query directly via Mediator
    query = GetPropertiesCatalogQuery(limit=10)
    catalog = await mediator.send(query)
    assert isinstance(catalog, list)
