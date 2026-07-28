# Observabilidade — Fono System

Observabilidade não é "adicionar logs depois" — é decisão de arquitetura que,
se deixada pra depois, vira reescrita. Três pilares: **logs, métricas e tracing**.

---

## Logs estruturados

`structlog` em vez de `print`/`logging` puro — cada log sai como JSON, com
campos consistentes (`clinica_id`, `usuario_id`, `correlation_id`, `acao`).

```python
logger.info("paciente_criado", paciente_id=p.id, clinica_id=c.id)
```

Cada requisição HTTP ganha um correlation ID único
(`interface/middlewares/correlation_id.py`), que propaga por todos os logs
daquela requisição — inclusive nas chamadas ao banco.

**Relação com auditoria:** logs estruturados e `logs_acesso`
(ver `docs/seguranca.md`) são coisas diferentes — log é operacional (debug,
performance), auditoria é rastro legal/compliance de quem acessou dado
sensível. Nascem do mesmo middleware, mas vão pra destinos diferentes.

---

## Métricas

Prometheus (self-hosted, roda na VPS junto do resto) expondo `/metrics`.

O que medir desde o início: latência por endpoint, taxa de erro (4xx/5xx),
tempo de query no banco, número de requisições por `clinica_id` — útil pra
entender uso real quando o sistema virar produto pra outras fonoaudiólogas.

**Alternativa considerada:** serviço gerenciado (Datadog, Better Stack) — mais
fácil de configurar, mas custo recorrente em dólar desde o dia 1. Prometheus +
Grafana mantém a filosofia self-hosted do resto da infra.

---

## Tracing

OpenTelemetry, instrumentando FastAPI e SQLAlchemy automaticamente.

Num sistema multi-tenant, tracing é o que permite ver "essa requisição lenta é
de qual clínica, em qual query especificamente" — sem isso, debugar
performance em produção é adivinhação. Entra depois de logs e métricas
estarem de pé.

---

## Health checks e alerting

`/health` (liveness) e `/ready` (checa Postgres, MinIO, Redis) desde a Fase 0.
Alerting simples no início: e-mail/Telegram se `/health` falhar ou taxa de
erro passar de um limite.

---

## Referência cruzada

- Onde esses middlewares vivem na estrutura: `docs/estrutura.md`
- Fase do roadmap em que isso entra: `docs/plano.md`
