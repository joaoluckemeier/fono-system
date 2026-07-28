from openai import AsyncOpenAI

from backend.config import Settings
from backend.domain.services.ai_gateway_service import AIGatewayInterface

_SYSTEM_PROMPT = """Voce e um assistente que transforma a transcricao de uma sessao de \
fonoaudiologia em um rascunho de evolucao clinica, em portugues formal, terceira pessoa \
("o paciente", "a paciente").

Regras rigidas:
- Baseie-se exclusivamente no que foi dito na transcricao. Nunca invente informacao, \
diagnostico ou observacao clinica que nao esteja no texto.
- Se a transcricao for confusa, incompleta ou nao contiver informacao clinica relevante, \
diga isso explicitamente no rascunho em vez de preencher lacunas.
- Nao inclua nomes proprios - use apenas "o paciente"/"a paciente".
- Retorne so o texto da evolucao, sem titulo, sem markdown, sem comentario adicional.
- Este texto e sempre um RASCUNHO que sera revisado por um profissional humano antes de \
virar registro oficial - nunca afirme conclusoes definitivas."""


class OpenAIGatewayService(AIGatewayInterface):
    def __init__(self, settings: Settings) -> None:
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def gerar_rascunho(self, contexto_sanitizado: str) -> str:
        resposta = await self._client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.2,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": contexto_sanitizado},
            ],
        )
        texto = resposta.choices[0].message.content
        return texto.strip() if texto else ""
