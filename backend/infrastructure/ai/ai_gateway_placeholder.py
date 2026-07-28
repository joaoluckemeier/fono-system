from backend.domain.services.ai_gateway_service import AIGatewayInterface
from backend.domain.services.transcricao_service import TranscricaoServiceInterface


class AIGatewayPlaceholder(AIGatewayInterface):
    """Usado quando AI_GATEWAY_MODO=placeholder (sem OPENAI_API_KEY configurada)."""

    async def gerar_rascunho(self, contexto_sanitizado: str) -> str:
        raise NotImplementedError("AI_GATEWAY_MODO=placeholder - configure OPENAI_API_KEY para usar IA")


class TranscricaoServicePlaceholder(TranscricaoServiceInterface):
    async def transcrever(self, audio_bytes: bytes, nome_arquivo: str) -> str:
        raise NotImplementedError("AI_GATEWAY_MODO=placeholder - configure OPENAI_API_KEY para usar IA")
