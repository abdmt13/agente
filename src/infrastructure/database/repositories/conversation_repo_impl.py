from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select, delete, desc, asc
from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.domain.entities.conversation import Conversation
from src.domain.entities.message import Message
from src.infrastructure.database.models.conversation_model import ConversationModel
from src.infrastructure.database.models.message_model import MessageModel
from src.interfaces.ports.repositories.conversation_repository import IConversationRepository


class ConversationRepositoryImpl(IConversationRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    def _to_conversation_entity(self, model: ConversationModel) -> Conversation:
        messages = [
            Message(
                id=m.id,
                session_id=m.session_id,
                role=m.role,
                content=m.content,
                created_at=m.created_at
            )
            for m in (model.messages or [])
        ]
        return Conversation(
            session_id=model.session_id,
            previous_response_id=model.previous_response_id,
            created_at=model.created_at,
            messages=messages
        )

    async def get_by_session_id(self, session_id: str) -> Optional[Conversation]:
        stmt = (
            select(ConversationModel)
            .options(selectinload(ConversationModel.messages))
            .where(ConversationModel.session_id == session_id)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_conversation_entity(model) if model else None

    async def save_turn(
        self,
        session_id: str,
        user_message: str,
        assistant_reply: str,
        previous_response_id: Optional[str] = None
    ) -> None:
        # 1. Asegurar o crear la conversación
        stmt = select(ConversationModel).where(ConversationModel.session_id == session_id)
        result = await self._session.execute(stmt)
        conv_model = result.scalar_one_or_none()

        now = datetime.now(timezone.utc)
        if not conv_model:
            conv_model = ConversationModel(
                session_id=session_id,
                previous_response_id=previous_response_id,
                created_at=now
            )
            self._session.add(conv_model)
        else:
            if previous_response_id is not None:
                conv_model.previous_response_id = previous_response_id

        # 2. Agregar mensajes
        user_msg_model = MessageModel(
            session_id=session_id,
            role="user",
            content=user_message,
            created_at=now
        )
        assistant_msg_model = MessageModel(
            session_id=session_id,
            role="assistant",
            content=assistant_reply,
            created_at=now
        )

        self._session.add(user_msg_model)
        self._session.add(assistant_msg_model)
        await self._session.flush()

    async def get_messages(
        self,
        session_id: str,
        recent_only: bool = False,
        limit: int = 20
    ) -> List[Message]:
        if recent_only:
            # Subquery o selección descendente invertida
            stmt = (
                select(MessageModel)
                .where(MessageModel.session_id == session_id)
                .order_by(desc(MessageModel.id))
                .limit(limit)
            )
            result = await self._session.execute(stmt)
            models = list(result.scalars().all())
            models.reverse()
        else:
            stmt = (
                select(MessageModel)
                .where(MessageModel.session_id == session_id)
                .order_by(asc(MessageModel.id))
            )
            result = await self._session.execute(stmt)
            models = list(result.scalars().all())

        return [
            Message(
                id=m.id,
                session_id=m.session_id,
                role=m.role,
                content=m.content,
                created_at=m.created_at
            )
            for m in models
        ]

    async def delete_conversation(self, session_id: str) -> bool:
        await self._session.execute(delete(MessageModel).where(MessageModel.session_id == session_id))
        stmt = delete(ConversationModel).where(ConversationModel.session_id == session_id)
        result = await self._session.execute(stmt)
        await self._session.flush()
        rowcount = result.rowcount if isinstance(result, CursorResult) else 0
        return bool(rowcount > 0)
