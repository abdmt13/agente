from typing import List, Optional
import httpx
import structlog
from src.domain.entities.message import Message
from src.interfaces.ports.ai_service import IAIService

logger = structlog.get_logger()


class AIServiceAdapter(IAIService):
    def __init__(
        self,
        provider: str = "gemini",
        gemini_api_key: Optional[str] = None,
        gemini_model: str = "gemini-2.5-flash",
        openai_api_key: Optional[str] = None,
        openai_model: str = "gpt-4o-mini",
        timeout_ms: int = 15000
    ):
        self.provider = provider
        self.gemini_api_key = gemini_api_key
        self.gemini_model = gemini_model
        self.openai_api_key = openai_api_key
        self.openai_model = openai_model
        self.timeout = timeout_ms / 1000.0

    async def generate_reply(
        self,
        user_message: str,
        history: List[Message],
        system_instruction: str,
        previous_response_id: Optional[str] = None
    ) -> tuple[str, Optional[str]]:
        """Llama al proveedor configurado o entrega una respuesta local en modo demo."""
        if self.provider == "gemini" and self.gemini_api_key:
            return await self._call_gemini(user_message, history, system_instruction)
        elif self.provider == "openai" and self.openai_api_key:
            return await self._call_openai(user_message, history, system_instruction)

        # Fallback de demostración si no hay llaves configuradas
        return (
            f"[MODO DEMO] Has dicho: '{user_message}'. Para respuestas inteligentes completas, configure GEMINI_API_KEY o OPENAI_API_KEY en su archivo .env.",
            None
        )

    async def _call_gemini(
        self,
        user_message: str,
        history: List[Message],
        system_instruction: str
    ) -> tuple[str, Optional[str]]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.gemini_model}:generateContent?key={self.gemini_api_key}"
        
        contents = []
        for msg in history:
            role = "user" if msg.role == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg.content}]})
        
        contents.append({"role": "user", "parts": [{"text": user_message}]})

        payload = {
            "contents": contents,
            "systemInstruction": {
                "parts": [{"text": system_instruction}]
            }
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                reply = data["candidates"][0]["content"]["parts"][0]["text"]
                return reply.strip(), None
            except Exception as e:
                logger.error("Error llamando a Gemini API", error=str(e))
                return "Disculpa, ocurrió un inconveniente conectando con el servicio de IA.", None

    async def _call_openai(
        self,
        user_message: str,
        history: List[Message],
        system_instruction: str
    ) -> tuple[str, Optional[str]]:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        messages = [{"role": "system", "content": system_instruction}]
        for msg in history:
            messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": user_message})

        payload = {
            "model": self.openai_model,
            "messages": messages
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                reply = data["choices"][0]["message"]["content"]
                return reply.strip(), None
            except Exception as e:
                logger.error("Error llamando a OpenAI API", error=str(e))
                return "Disculpa, ocurrió un inconveniente conectando con el servicio de IA.", None
