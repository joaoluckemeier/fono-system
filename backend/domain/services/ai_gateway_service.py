from abc import ABC, abstractmethod


class AIGatewayInterface(ABC):
    """Ver docs/ia-preparacao.md.

    Nenhum texto gerado por IA vira evolucao clinica oficial sem revisao humana.
    """

    @abstractmethod
    async def gerar_rascunho(self, contexto_sanitizado: str) -> str:
        """Retorna texto em estado pendente_revisao. Nunca grava direto no banco."""
