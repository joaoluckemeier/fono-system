from abc import ABC, abstractmethod


class GeradorDocumentoInterface(ABC):
    """O dominio nao sabe qual biblioteca gera o PDF - so chama a interface."""

    @abstractmethod
    async def gerar_pdf(self, titulo: str, corpo_texto: str) -> bytes: ...
