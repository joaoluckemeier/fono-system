# Plano de implementação — Fono System

Fases sequenciais. Cada fase só começa quando a anterior está funcionando e
verificada localmente.

---

## FASE 0 — Fundação do backend

**Objetivo:** projeto rodando, banco conectado, nenhuma funcionalidade de
negócio ainda.

**O que fazer:**
- Criar estrutura de pastas completa (ver `docs/estrutura.md`)
- `pyproject.toml` + `uv.lock` (ver `docs/supply-chain.md`):
  ```
  fastapi==0.115.0
  uvicorn[standard]==0.30.0
  sqlalchemy[asyncio]==2.0.35
  asyncpg==0.29.0
  alembic==1.13.3
  pydantic[email]==2.9.2
  python-jose[cryptography]==3.3.0
  argon2-cffi==23.1.0
  python-dotenv==1.0.1
  slowapi==0.1.9
  structlog==24.4.0
  prometheus-client==0.21.0
  ```
- `backend/config.py` — lê `.env` e expõe objeto tipado
- `infrastructure/database/connection.py` — engine async + session factory
- `infrastructure/database/models/base.py` — Mixin com campos comuns
- `docker-compose.yml` — API + Postgres + MinIO + Redis
- HTTPS local (mkcert) + CI com `pip-audit` + `Trivy` + pre-commit (lint,
  format, testes rápidos, scan de segredo)
- Imagem Docker `slim` + usuário não-root (ver `docs/supply-chain.md`)
- `.env` + `.env.example` + `.gitignore`
- `backend/main.py` — FastAPI básico com healthcheck

**Verificar:**
```bash
docker compose up -d
uv run uvicorn backend.main:app --reload
# GET http://localhost:8000/health → {"status": "ok"}
```

**Entregável:** servidor no ar, banco/MinIO/Redis conectados, sem nenhuma
rota de negócio.

---

## FASE 1 — Domínio e banco

**Objetivo:** entidades, contratos e banco estruturado com migrations.

**O que fazer:**
- Entidades de domínio — `domain/entities/` (11 arquivos com enums Python)
- Interfaces de repositório — `domain/repositories/` (11 arquivos ABC)
- Interface de storage — `domain/services/storage_service.py`
- Interface de IA (placeholder) — `domain/services/ai_gateway_service.py`
  (ver `docs/ia-preparacao.md`)
- Política de autorização — `domain/authorization/policy.py` (ver `docs/seguranca.md`)
- Modelos ORM — `infrastructure/database/models/` (11 tabelas + base)
- Alembic configurado:
  ```bash
  alembic init alembic
  alembic revision --autogenerate -m "initial schema"
  alembic upgrade head
  ```

**Verificar:**
```bash
psql $DATABASE_URL -c "\dt"
# deve listar: clinicas, usuarios, pacientes, profissionais_caso, protocolos,
# protocolos_paciente, caa_dados, evolucoes, anexos, logs_acesso, refresh_tokens
```

**Entregável:** banco PostgreSQL com 11 tabelas criadas.

---

## FASE 2 — Autenticação, autorização e observabilidade base

**Objetivo:** login funcionando com JWT, RBAC ativo, logs estruturados desde
o primeiro commit. Construídos juntos — não depois, pra evitar retrofitting
doloroso em cima de dado já existente.

**O que fazer:**
- `infrastructure/repositories/usuario_repository.py`
- `infrastructure/repositories/clinica_repository.py`
- `infrastructure/repositories/refresh_token_repository.py`
- `application/dtos/auth_dto.py`
- `application/use_cases/auth/login.py`
- `application/use_cases/auth/refresh_token.py`
- `application/use_cases/auth/validar_token.py`
- `interface/schemas/auth_schema.py`
- `interface/routers/auth_router.py` — `POST /auth/login`, `POST /auth/refresh`
- `interface/dependencies.py` — `Depends(get_usuario_atual)`
- `interface/middlewares/` — correlation ID, rate limiting, auditoria
- `infrastructure/audit/audit_logger.py` — grava `logs_acesso`
- `infrastructure/observability/logging.py` — configuração `structlog`
- `backend/container.py` — primeira montagem com repositórios de auth
- CORS configurado no `main.py`
- Seed manual: inserir uma clínica e um usuário no banco para teste

**Verificar:**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "beta@clinica.com", "senha": "senha_teste"}'

curl http://localhost:8000/pacientes
# → {"detail": "Not authenticated"}

# 6 tentativas erradas → rate limit
# → {"error": "Rate limit exceeded"}
```

**Entregável:** autenticação com JWT + refresh, RBAC, auditoria e logging
estruturado funcionando.

---

## FASE 3 — Módulos de negócio

**Objetivo:** todos os endpoints da API implementados e testados via Swagger.

Para cada módulo, criar na ordem: repository (infra) → DTO → use cases →
schema → router → registrar no container → registrar no main.

### 3a — Pacientes
```
GET    /pacientes
POST   /pacientes
GET    /pacientes/{id}
PUT    /pacientes/{id}
DELETE /pacientes/{id}
```

### 3b — Profissionais do caso (depende de paciente)
```
GET    /pacientes/{id}/profissionais
POST   /pacientes/{id}/profissionais
DELETE /profissionais/{id}
```

### 3c — Protocolos (catálogo) e protocolos do paciente
```
GET    /protocolos
POST   /protocolos
GET    /pacientes/{id}/protocolos
POST   /pacientes/{id}/protocolos
```

### 3d — CAA (depende de paciente)
```
GET    /pacientes/{id}/caa
PUT    /pacientes/{id}/caa
```

### 3e — Evoluções (depende de paciente)
```
GET    /pacientes/{id}/evolucoes
POST   /pacientes/{id}/evolucoes
GET    /pacientes/{id}/evolucoes/ultima
```

### 3f — Anexos (implementar MinIOStorageService aqui)
```
GET    /anexos?entidade_tipo=&entidade_id=
POST   /anexos
DELETE /anexos/{id}
```

**Verificar:** abrir `http://localhost:8000/docs` e testar cada endpoint
manualmente com token JWT no header `Authorization: Bearer {token}`.

**Entregável:** todos os endpoints respondendo corretamente.

---

## FASE 4 — Testes

**Objetivo:** cobertura mínima que garante que o sistema não quebra
silenciosamente.

### Testes unitários (`tests/unit/`) — sem banco

```python
# test_login.py
def test_login_credenciais_corretas():
    repo_mock = UsuarioRepositoryMock(usuario_existente)
    use_case = LoginUseCase(repository=repo_mock)
    resultado = use_case.executar("beta@clinica.com", "senha_correta")
    assert resultado.token is not None
```

Arquivos mínimos:
- `test_login.py` — credenciais corretas, erradas, usuário inexistente
- `test_criar_paciente.py` — paciente válido, autorização por papel
- `test_soft_delete.py` — registro deletado não aparece em listagens
- `test_autorizacao.py` — secretaria não acessa diagnóstico/evolução

### Testes de integração (`tests/integration/`) — com banco de teste

```bash
DATABASE_URL=postgresql+asyncpg://usuario:senha@localhost:5432/fono_test
```

Arquivos mínimos:
- `test_paciente_repository.py` — CRUD + soft delete + filtro por clínica
- `test_evolucao_repository.py` — histórico + busca de última devolutiva

**Verificar:**
```bash
uv run pytest tests/unit/ -v
uv run pytest tests/integration/
```

**Entregável:** `pytest` rodando verde nos dois conjuntos.

---

## FASE 5 — Deploy no VPS

**Objetivo:** sistema em produção com HTTPS e dados persistidos.

### 5a — Docker Compose de produção

```yaml
services:
  backend:
    build: .
    env_file: .env
    depends_on: [db, minio, redis]
    ports: ["8000:8000"]

  db:
    image: postgres:16
    environment:
      POSTGRES_DB: fono
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes: [pgdata:/var/lib/postgresql/data]

  minio:
    image: minio/minio
    command: server /data
    volumes: [miniodata:/data]

  redis:
    image: redis:7-alpine

volumes:
  pgdata:
  miniodata:
```

### 5b — VPS e HTTPS

```bash
apt update && apt install -y docker.io docker-compose-plugin certbot
git clone ... && cd fono-backend
cp .env.example .env   # editar com valores reais de produção
docker compose up -d
certbot certonly --standalone -d api.fono.seudominio.com.br
echo "0 3 * * * pg_dump \$DATABASE_URL | gpg --encrypt | gzip > /backups/fono_\$(date +%Y%m%d).sql.gz.gpg" | crontab -
```

**VPS recomendado:** 2GB RAM (Postgres + MinIO + Redis juntos pedem mais
que só a API).

**Entregável:** sistema acessível via HTTPS, dados persistidos, backup
automático configurado.

---

## Fases futuras (fora da sequência acima)

| Fase | Entrega | Depende de |
|---|---|---|
| 6 | Exportação de relatório em PDF | Módulo de evoluções funcionando |
| 7 | Criptografia por coluna nos campos mais sensíveis | Exigência contratual/escala |
| 8 | Módulo de agenda (bounded context separado) | Validação de demanda real |
| 9 | Frontend consumindo a API | Fases 0-5 completas |
| 10 | Observabilidade avançada (Prometheus + Grafana + tracing) | Sistema com tráfego real — ver `docs/observabilidade.md` |
| 11 | Módulo de marketing (se aplicável ao negócio da clínica) | Fora do escopo atual |
| 12 | Primeira feature de IA + framework de evals | `AIGatewayInterface` com caso de uso real — ver `docs/ia-preparacao.md` |

---

## Resumo das fases

| Fase | Entrega | Estimativa |
|---|---|---|
| 0 — Fundação | Servidor FastAPI + Docker Compose no ar | 1 dia |
| 1 — Domínio e banco | Banco estruturado, 11 tabelas | 1-2 dias |
| 2 — Auth + RBAC + observabilidade | Login, JWT, refresh, RBAC, auditoria, logs | 2 dias |
| 3 — Módulos | Todos os endpoints | 4-6 dias |
| 4 — Testes | Cobertura mínima | 1-2 dias |
| 5 — Deploy | Sistema em produção | 1 dia |
| 6+ — Futuras | PDF, criptografia por coluna, agenda, frontend, IA | pós-lançamento |

---

## Decisões em aberto antes de iniciar

- **Protocolos**: catálogo por clínica (assumido) vs texto livre — confirmar
  com a Beta antes da Fase 1, ainda que a Fase 1 não fique bloqueada por isso.
- **Diagnóstico**: texto livre na v1 — confirmado.
