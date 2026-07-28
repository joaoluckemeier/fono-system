# CLAUDE.md — Fono System (Backend)

Sistema de gestão de pacientes e evoluções para clínica de fonoaudiologia.
Backend Python + FastAPI + PostgreSQL seguindo Clean Architecture.
Nasce multi-tenant (potencial de virar produto para outras fonoaudiólogas).

---

## Stack

- Python 3.12+ · FastAPI · SQLAlchemy 2.0 async · PostgreSQL 16
- Alembic (migrations) · Pydantic v2 · python-jose + argon2-cffi · slowapi
- MinIO (storage S3-compatible) · Redis (rate limit) · uv (deps + lockfile)

---

## Camadas — regra fundamental

Dependências só apontam de fora para dentro. Nunca o contrário.

```
[ domain/ ]  →  [ application/ ]  →  [ infrastructure/ ]  →  [ interface/ ]
  Entidades       Use cases            ORM / banco             Routers HTTP
  Interfaces      DTOs internos        Repositórios impl       Schemas Pydantic
  Contratos       Orquestração         Storage/AI/Audit impl   FastAPI
```

| Camada | Pode importar | Nunca importa |
|---|---|---|
| `domain/` | apenas stdlib Python | SQLAlchemy, FastAPI, Pydantic |
| `application/` | `domain/` | SQLAlchemy, FastAPI, Pydantic |
| `infrastructure/` | `domain/` | FastAPI, `application/`, routers |
| `interface/` | `application/` via container | `infrastructure/` diretamente |

`container.py` é o único arquivo que importa todas as camadas.
Detalhes: `docs/arquitetura.md`

---

## Regras críticas — SEMPRE

- Todo endpoint exige JWT — exceto `POST /auth/login`
- Toda query filtra `clinica_id` E `deletado == False`
- Soft delete via `repository.soft_delete(id, clinica_id)` — nunca DELETE direto
- Toda ação de autorização passa pela política central em `domain/authorization/` — nunca `if papel == "admin"` solto no router
- Leitura de dado clínico sensível (paciente, evolução) gera registro em `logs_acesso` — via middleware, automático
- Variáveis sensíveis via `os.getenv()` — nunca hardcodadas
- Fluxo obrigatório: `Router → schema → DTO → UseCase → Repository interface → impl`
- Toda dependência nova entra via `uv add`, nunca `pip install` solto — lockfile sempre commitado

## Regras críticas — NUNCA

- SQL raw concatenado com string de usuário
- `eval()` ou `exec()` com input externo
- Secrets no código ou no Git
- Lógica de negócio no router
- SQLAlchemy fora de `infrastructure/`
- FastAPI fora de `interface/`
- Pydantic fora de `interface/schemas/`
- Texto gerado por IA persistido em `evolucoes` sem estado `pendente_revisao` + confirmação humana — ver `docs/ia-preparacao.md`

---

## Padrão de resposta

```json
{ "data": { ... }, "message": "ok" }
{ "detail": "mensagem de erro legível" }
```

---

## Referências

- Arquitetura completa, container, enums, DTOs vs Schemas → `docs/arquitetura.md`
- Estrutura de pastas com explicação de cada uma → `docs/estrutura.md`
- Modelagem do banco (11 tabelas) → `docs/modelagem.md`
- Segurança por fase de risco → `docs/seguranca.md`
- Gestão de pacotes e supply chain → `docs/supply-chain.md`
- Observabilidade (logs, métricas, tracing) → `docs/observabilidade.md`
- Preparação arquitetural para IA (gateway, hooks, evals) → `docs/ia-preparacao.md`
- Plano de implementação (fases) → `docs/plano.md`
