import re
from datetime import datetime
from typing import List
from src.domain.exceptions.conversation import InvalidSessionException
from src.interfaces.ports.unit_of_work import IUnitOfWork
from src.interfaces.ports.cache_service import ICacheService
from src.interfaces.dtos.chat_dto import ChatMessageDTO, ConversationHistoryDTO


class GetConversationUseCase:
    def __init__(self, uow: IUnitOfWork, cache_service: ICacheService):
        self._uow = uow
        self._cache_service = cache_service

    async def execute(self, session_id: str, recent_only: bool = False, limit: int = 20) -> ConversationHistoryDTO:
        session_id = session_id.strip()
        if not session_id or len(session_id) > 100 or not re.match(r"^[\x00-\x7F]+$", session_id):
            raise InvalidSessionException(session_id)

        cache_key = f"conv:{session_id}:recent={recent_only}:limit={limit}"
        cached = await self._cache_service.get(cache_key)
        if cached:
            messages = [
                ChatMessageDTO(
                    id=m.get("id"),
                    session_id=m["session_id"],
                    role=m["role"],
                    content=m["content"],
                    created_at=datetime.fromisoformat(m["created_at"]) if m.get("created_at") else None
                )
                for m in cached
            ]
            return ConversationHistoryDTO(session_id=session_id, messages=messages)

        async with self._uow as uow:
            msg_entities = await uow.conversations.get_messages(session_id=session_id, recent_only=recent_only, limit=limit)
            dtos = [
                ChatMessageDTO(
                    id=m.id,
                    session_id=m.session_id,
                    role=m.role,
                    content=m.content,
                    created_at=m.created_at
                )
                for m in msg_entities
            ]

            # Guardar en cache por 60s
            await self._cache_service.set(
                cache_key,
                [{"id": d.id, "session_id": d.session_id, "role": d.role, "content": d.content, "created_at": d.created_at.isoformat() if d.created_at else None} for d in dtos],
                ttl_seconds=60
            )

            return ConversationHistoryDTO(session_id=session_id, messages=dtos)


class DeleteConversationUseCase:
    def __init__(self, uow: IUnitOfWork, cache_service: ICacheService):
        self._uow = uow
        self._cache_service = cache_service

    async def execute(self, session_id: str) -> bool:
        session_id = session_id.strip()
        if not session_id or len(session_id) > 100 or not re.match(r"^[\x00-\x7F]+$", session_id):
            raise InvalidSessionException(session_id)

        async with self._uow as uow:
            deleted = await uow.conversations.delete_conversation(session_id=session_id)
            await uow.commit()

        await self._cache_service.delete(f"conv:{session_id}")
        await self._cache_service.delete(f"conv:{session_id}:recent=False:limit=20")
        await self._cache_service.delete(f"conv:{session_id}:recent=True:limit=20")
        return deleted
