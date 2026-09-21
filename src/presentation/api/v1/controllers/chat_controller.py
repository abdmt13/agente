from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from src.application.commands.chat_commands import (
    SendMessageCommand,
    DeleteConversationCommand,
)
from src.application.queries.chat_queries import GetConversationHistoryQuery
from src.application.mediator.mediator import Mediator
from src.domain.exceptions.base import DomainException
from src.presentation.api.dependencies.mediator_dep import get_mediator
from src.presentation.api.dtos.chat_requests import (
    SendMessageBody,
    SendMessageRequestDTO,
    GetHistoryRequestDTO,
    DeleteConversationRequestDTO,
)

router = APIRouter(tags=["Chatbot"])


def get_send_message_dto(body: SendMessageBody) -> SendMessageRequestDTO:
    return SendMessageRequestDTO(session_id=body.sessionId, message=body.message)


def get_history_dto(
    sessionId: str = Path(..., description="ID de sesión de la conversación"),
    recentOnly: bool = Query(False, description="Solo mensajes recientes"),
    limit: int = Query(20, ge=1, le=100, description="Límite de mensajes")
) -> GetHistoryRequestDTO:
    return GetHistoryRequestDTO(session_id=sessionId, recent_only=recentOnly, limit=limit)


def get_delete_dto(
    sessionId: str = Path(..., description="ID de sesión a eliminar")
) -> DeleteConversationRequestDTO:
    return DeleteConversationRequestDTO(session_id=sessionId)


@router.post("/chat", summary="Enviar mensaje al chatbot")
async def send_message(
    dto: SendMessageRequestDTO = Depends(get_send_message_dto),
    mediator: Mediator = Depends(get_mediator),
) -> Dict[str, Any]:
    """Controlador que solo despacha al Mediator."""
    try:
        command = SendMessageCommand(
            session_id=dto.session_id,
            message=dto.message
        )
        result = await mediator.send(command)
        return {
            "reply": result.reply,
            "sessionId": result.session_id,
            "demo": result.demo,
            "responseId": result.response_id
        }
    except DomainException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error inesperado: {str(e)}")


@router.get("/chat/{sessionId}", summary="Obtener historial de mensajes")
async def get_messages(
    dto: GetHistoryRequestDTO = Depends(get_history_dto),
    mediator: Mediator = Depends(get_mediator),
) -> Dict[str, Any]:
    """Controlador que solo despacha al Mediator."""
    try:
        query = GetConversationHistoryQuery(
            session_id=dto.session_id,
            recent_only=dto.recent_only,
            limit=dto.limit
        )
        result = await mediator.send(query)
        return {
            "sessionId": result.session_id,
            "messages": [
                {
                    "id": m.id,
                    "role": m.role,
                    "content": m.content,
                    "createdAt": m.created_at.isoformat() if hasattr(m.created_at, "isoformat") else (str(m.created_at) if m.created_at else None)
                }
                for m in result.messages
            ]
        }
    except DomainException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/chat/{sessionId}", summary="Eliminar conversación")
async def delete_conversation(
    dto: DeleteConversationRequestDTO = Depends(get_delete_dto),
    mediator: Mediator = Depends(get_mediator),
) -> Dict[str, Any]:
    """Controlador que solo despacha al Mediator."""
    try:
        command = DeleteConversationCommand(session_id=dto.session_id)
        result = await mediator.send(command)
        return {"ok": result}
    except DomainException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
