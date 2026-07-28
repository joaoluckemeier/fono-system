# IA — Preparação arquitetural — Fono System

Módulo **não construído** nesta fase — este doc registra o padrão arquitetural
preparado desde já pra que a primeira feature de IA (ex: rascunho assistido de
evolução clínica) não exija reescrita de nada quando for implementada. Mesmo
princípio já usado no projeto para `StorageServiceInterface` (ver
`docs/arquitetura.md`): uma interface hoje, implementação quando fizer sentido.

---

## Por que existe agora, sem feature construída

Regra inegociável do sistema: nenhum texto gerado por IA pode virar evolução
clínica oficial sem revisão humana explícita. A IA, quando existir, só pode
gerar rascunho em estado `pendente_revisao` — a fonoaudióloga confirma antes
de virar registro. Isso não é só boa prática, é o que separa "ferramenta de
apoio" de "risco de erro clínico documentado incorretamente".

Preparar o gateway agora, mesmo sem uso real, garante que essa regra vive
estrutural na arquitetura — não depende de alguém lembrar de aplicá-la quando
a feature for escrita sob pressão de prazo.

---

## Camadas (Clean Architecture, mesmo padrão de todo módulo do projeto)

| Camada | Arquivo | Status |
|---|---|---|
| Interface de serviço externo (ponto de troca placeholder/real) | `backend/domain/services/ai_gateway_service.py` | A criar na Fase 0 — interface apenas |
| Implementação placeholder | `backend/infrastructure/ai/ai_gateway_placeholder.py` | `NotImplementedError` em todos os métodos |
| Implementação real (futura) | `backend/infrastructure/ai/real_ai_gateway_service.py` | Não existe até haver caso de uso real |
| Use case (futuro) | `backend/application/use_cases/evolucoes/gerar_rascunho_evolucao.py` | Não existe até a Fase 12 do roadmap |
| Domain events (base pra hooks futuros) | `backend/domain/events/` | `EvolucaoCriada`, `PacienteCadastrado` — emitidos desde a v1, sem listener além de log |

---

## Hooks de LLM — pré e pós-chamada

Desenhados como parte do `AIGatewayInterface`, não espalhados pelo código:

- **Pré-chamada**: sanitização — nenhum dado de paciente sai pra uma API de IA
  de terceiros sem passar por anonimização/minimização (remover nome completo,
  manter só o necessário pro contexto clínico).
- **Pós-chamada**: validação do output antes de aceitar — nunca um texto
  gerado vira dado persistido sem checagem estrutural (campos obrigatórios
  presentes, tamanho razoável) e, no caso de evolução clínica, sem revisão
  humana explícita.

```python
# domain/services/ai_gateway_service.py
from abc import ABC, abstractmethod

class AIGatewayInterface(ABC):
    @abstractmethod
    def gerar_rascunho(self, contexto_sanitizado: str) -> str:
        """Retorna texto em estado pendente_revisao. Nunca grava direto no banco."""
```

---

## Configuração (`.env` / `.env.example` / `backend/config.py`) — reservada, não usada ainda

```
AI_GATEWAY_MODO=placeholder              # "placeholder" | "real"
AI_GATEWAY_PROVIDER=                     # não usado enquanto modo=placeholder
AI_GATEWAY_API_KEY=                      # idem
```

---

## Quando implementar a primeira feature real

1. Implementar `RealAIGatewayService.gerar_rascunho(...)` em
   `backend/infrastructure/ai/real_ai_gateway_service.py` (hoje só levantaria
   `NotImplementedError`).
2. Preencher `AI_GATEWAY_PROVIDER` e `AI_GATEWAY_API_KEY` no `.env`.
3. Trocar `AI_GATEWAY_MODO=real` em `container.py`.
4. Construir o framework de evals **antes** de ir pra produção — não faz
   sentido construir avaliação antes de existir o que avaliar:
   - Conjunto de exemplos reais (anonimizados) com resultado esperado, rodado
     contra o modelo antes de cada mudança de prompt ou de modelo.
   - Métrica central: fidelidade às observações originais, sem inventar
     informação clínica não dita (alucinação é o risco central aqui, mais do
     que em qualquer outro domínio).

Nenhuma outra camada muda — banco, use cases existentes e routers permanecem
intactos. Mesmo princípio de inversão de dependência já usado pra trocar
`LocalStorage` por `S3` (ver `docs/arquitetura.md`).

---

## Referência cruzada

- Fase futura no roadmap (Fase 12): `docs/plano.md`
- Regra "nunca" relacionada: `docs/seguranca.md`
