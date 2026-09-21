import re
import unicodedata
from typing import List, Optional
from src.domain.exceptions.conversation import InvalidSessionException, MessageTooLongException
from src.interfaces.ports.unit_of_work import IUnitOfWork
from src.interfaces.ports.ai_service import IAIService
from src.interfaces.ports.cache_service import ICacheService
from src.interfaces.ports.event_publisher import IEventPublisher
from src.interfaces.dtos.chat_dto import ChatResponseDTO
from src.infrastructure.config.settings import Settings


def _normalize_text(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower()


def _check_catalog_direct_reply(message: str, properties: list, truncated: bool) -> Optional[str]:
    text = _normalize_text(message)
    coastal = bool(
        re.search(r"\b(costa|playa|mar)\b", text)
        and re.search(r"\b(propiedad|casa|departamento|terreno|inmueble)\b", text)
    )
    general = bool(
        re.search(
            r"(?:(?:cuales|que)\s+(?:son\s+)?(?:las\s+)?(?:propiedades\s+|opciones\s+|casas\s+)?(?:disponibles|tienen)|que\s+(?:propiedades|opciones|casas)\s+(?:hay|tienen))[?¿.!\s]*$",
            text
        )
        and not (
            re.search(r"\b(presupuesto|menos|hasta|recamaras|zona|costa|playa|departamento|terreno)\b", text)
            or re.search(r"\d", text)
        )
    )
    if not coastal and not general:
        return None

    if coastal:
        return "Necesitamos confirmar qué opciones están cerca de la playa y sus precios antes de compararlas con tu presupuesto. ¿Qué ciudad o playa te interesa?"

    if not properties:
        return "Por ahora no tenemos propiedades disponibles para mostrarte."

    options = []
    for p in properties[:5]:
        dev_text = f", en {p.desarrollo.nombre}" if p.desarrollo else ""
        loc = ", ".join(filter(None, [p.desarrollo.ciudad if p.desarrollo else None, p.desarrollo.zona if p.desarrollo else None])) or "ubicación por confirmar"
        options.append(f"{p.nombre}{dev_text}: {p.tipo}, {loc}.")

    prefix = "Estas son algunas opciones" if (truncated or len(properties) > 5) else "Estas son las opciones"
    return f"{prefix} disponibles:\n\n" + "\n\n".join(options) + "\n\nLos precios están pendientes de confirmación con un asesor. ¿Qué opción te interesa?"


def _sanitize_customer_reply(reply: str, internal_codes: List[str]) -> str:
    technical = re.search(
        r"base\s+de\s+datos|\b(?:backend|mysql|sql|json|gemini|openai|api|prompt|prompts|GEMINI_API_KEY|OPENAI_API_KEY)\b",
        reply,
        re.IGNORECASE
    )
    has_code = any(code and code.lower() in reply.lower() for code in internal_codes)
    if technical or has_code:
        return "Necesito confirmar algunos detalles para orientarte mejor. ¿Qué característica es la más importante para ti en tu próxima propiedad?"
    return reply


class SendChatMessageUseCase:
    def __init__(
        self,
        uow: IUnitOfWork,
        ai_service: IAIService,
        cache_service: ICacheService,
        event_publisher: IEventPublisher,
        settings: Settings
    ):
        self._uow = uow
        self._ai_service = ai_service
        self._cache_service = cache_service
        self._event_publisher = event_publisher
        self._settings = settings

    async def execute(self, session_id: str, message: str) -> ChatResponseDTO:
        session_id = session_id.strip()
        message = message.strip()

        if not session_id or len(session_id) > 100 or not re.match(r"^[\x00-\x7F]+$", session_id):
            raise InvalidSessionException(session_id)

        if not message:
            raise InvalidSessionException("El mensaje no puede estar vacío.")

        if len(message) > 4000:
            raise MessageTooLongException(4000)

        async with self._uow as uow:
            # 1. Obtener catálogo y propiedades
            properties, truncated = await uow.properties.get_available_properties(limit=51)
            faqs = await uow.properties.get_active_faqs(limit=30)
            internal_codes = [p.codigo for p in properties]

            # 2. Verificar respuesta directa del catálogo
            direct_reply = _check_catalog_direct_reply(message, properties, truncated)
            if direct_reply:
                await uow.conversations.save_turn(
                    session_id=session_id,
                    user_message=message,
                    assistant_reply=direct_reply,
                    previous_response_id=None
                )
                await uow.commit()

                # Publicar evento
                await self._event_publisher.publish(
                    topic=self._settings.KAFKA_TOPIC_CHAT_EVENTS,
                    event_type="chat_message_processed",
                    data={"session_id": session_id, "mode": "direct_catalog"}
                )

                return ChatResponseDTO(
                    reply=direct_reply,
                    session_id=session_id,
                    demo=False,
                    response_id=None
                )

            # 3. Obtener historial reciente
            history = await uow.conversations.get_messages(session_id=session_id, recent_only=True, limit=20)
            conv = await uow.conversations.get_by_session_id(session_id=session_id)
            prev_resp_id = conv.previous_response_id if conv else None

            # 4. Construir prompt e instrucciones de negocio
            catalog_summary = [
                {
                    "nombre": p.nombre,
                    "tipo": p.tipo,
                    "recamaras": p.recamaras,
                    "banos": str(p.banos),
                    "construccion_m2": str(p.construccion_m2) if p.construccion_m2 else None,
                    "terreno_m2": str(p.terreno_m2) if p.terreno_m2 else None,
                    "desarrollo": p.desarrollo.nombre if p.desarrollo else None,
                    "ciudad": p.desarrollo.ciudad if p.desarrollo else None,
                    "zona": p.desarrollo.zona if p.desarrollo else None,
                }
                for p in properties
            ]
            faqs_summary = [{"pregunta": f.pregunta, "respuesta": f.respuesta} for f in faqs]

            system_instruction = (
                f"{self._settings.BOT_INSTRUCTIONS}\n"
                f"Catálogo de propiedades disponibles (truncated={truncated}): {catalog_summary}\n"
                f"Preguntas frecuentes: {faqs_summary}\n"
                f"Reglas: Si truncated es true, las opciones son parciales y no puedes descartar otras."
            )

            # 5. Generar respuesta con IA
            raw_reply, resp_id = await self._ai_service.generate_reply(
                user_message=message,
                history=history,
                system_instruction=system_instruction,
                previous_response_id=prev_resp_id
            )

            # 6. Filtrar y sanitizar respuesta de cliente
            reply = _sanitize_customer_reply(raw_reply, internal_codes)

            # 7. Persistir turno
            await uow.conversations.save_turn(
                session_id=session_id,
                user_message=message,
                assistant_reply=reply,
                previous_response_id=resp_id
            )
            await uow.commit()

            # 8. Invalidar / actualizar caché
            await self._cache_service.delete(f"conv:{session_id}")

            # 9. Publicar evento a Kafka
            await self._event_publisher.publish(
                topic=self._settings.KAFKA_TOPIC_CHAT_EVENTS,
                event_type="chat_message_processed",
                data={"session_id": session_id, "mode": "ai_reply"}
            )

            is_demo = not bool(self._settings.GEMINI_API_KEY or self._settings.OPENAI_API_KEY)

            return ChatResponseDTO(
                reply=reply,
                session_id=session_id,
                demo=is_demo,
                response_id=resp_id
            )
