from openai import AsyncOpenAI

from backend.config import Settings
from backend.domain.services.transcricao_service import TranscricaoServiceInterface

TAMANHO_MAXIMO_BYTES = 25 * 1024 * 1024  # limite da API de audio da OpenAI


class OpenAITranscricaoService(TranscricaoServiceInterface):
    def __init__(self, settings: Settings) -> None:
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def transcrever(self, audio_bytes: bytes, nome_arquivo: str) -> str:
        if len(audio_bytes) > TAMANHO_MAXIMO_BYTES:
            raise ValueError("Arquivo de audio excede o limite de 25MB da API de transcricao")

        resposta = await self._client.audio.transcriptions.create(
            model="whisper-1",
            file=(nome_arquivo, audio_bytes),
            language="pt",
        )
        return resposta.text
