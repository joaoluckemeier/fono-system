from abc import ABC, abstractmethod


class TranscricaoServiceInterface(ABC):
    """Audio da sessao -> texto. Separado de AIGatewayInterface (texto -> rascunho)
    porque sao dois passos independentes com fornecedores potencialmente diferentes."""

    @abstractmethod
    async def transcrever(self, audio_bytes: bytes, nome_arquivo: str) -> str: ...
