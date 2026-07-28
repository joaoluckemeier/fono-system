# Estrutura de pastas — Fono System

## Árvore completa

```
fono-backend/
│
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── container.py
│   │
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── clinica.py
│   │   │   ├── usuario.py
│   │   │   ├── paciente.py
│   │   │   ├── profissional_caso.py
│   │   │   ├── protocolo.py
│   │   │   ├── protocolo_paciente.py
│   │   │   ├── caa_dados.py
│   │   │   ├── evolucao.py
│   │   │   ├── anexo.py
│   │   │   ├── log_acesso.py
│   │   │   └── refresh_token.py
│   │   ├── repositories/
│   │   │   ├── base_repository.py
│   │   │   ├── clinica_repository.py
│   │   │   ├── usuario_repository.py
│   │   │   ├── paciente_repository.py
│   │   │   ├── profissional_caso_repository.py
│   │   │   ├── protocolo_repository.py
│   │   │   ├── protocolo_paciente_repository.py
│   │   │   ├── caa_dados_repository.py
│   │   │   ├── evolucao_repository.py
│   │   │   ├── anexo_repository.py
│   │   │   ├── log_acesso_repository.py
│   │   │   └── refresh_token_repository.py
│   │   ├── services/
│   │   │   ├── storage_service.py
│   │   │   └── ai_gateway_service.py
│   │   └── authorization/
│   │       └── policy.py
│   │
│   ├── application/
│   │   ├── dtos/
│   │   │   ├── auth_dto.py
│   │   │   ├── paciente_dto.py
│   │   │   ├── profissional_caso_dto.py
│   │   │   ├── protocolo_dto.py
│   │   │   ├── protocolo_paciente_dto.py
│   │   │   ├── caa_dados_dto.py
│   │   │   ├── evolucao_dto.py
│   │   │   └── anexo_dto.py
│   │   └── use_cases/
│   │       ├── auth/
│   │       │   ├── login.py
│   │       │   ├── refresh_token.py
│   │       │   └── validar_token.py
│   │       ├── pacientes/
│   │       │   ├── criar_paciente.py
│   │       │   ├── listar_pacientes.py
│   │       │   ├── buscar_paciente.py
│   │       │   ├── atualizar_paciente.py
│   │       │   └── deletar_paciente.py
│   │       ├── profissionais_caso/
│   │       │   ├── criar_profissional.py
│   │       │   ├── listar_profissionais.py
│   │       │   └── deletar_profissional.py
│   │       ├── protocolos/
│   │       │   ├── criar_protocolo.py
│   │       │   ├── listar_protocolos.py
│   │       │   ├── associar_protocolo_paciente.py
│   │       │   └── listar_protocolos_paciente.py
│   │       ├── caa/
│   │       │   ├── atualizar_caa.py
│   │       │   └── buscar_caa.py
│   │       ├── evolucoes/
│   │       │   ├── criar_evolucao.py
│   │       │   ├── listar_evolucoes.py
│   │       │   └── buscar_ultima_devolutiva.py
│   │       └── anexos/
│   │           ├── criar_anexo.py
│   │           ├── listar_anexos.py
│   │           └── deletar_anexo.py
│   │
│   ├── infrastructure/
│   │   ├── database/
│   │   │   ├── connection.py
│   │   │   └── models/
│   │   │       ├── base.py
│   │   │       ├── clinica_model.py
│   │   │       ├── usuario_model.py
│   │   │       ├── paciente_model.py
│   │   │       ├── profissional_caso_model.py
│   │   │       ├── protocolo_model.py
│   │   │       ├── protocolo_paciente_model.py
│   │   │       ├── caa_dados_model.py
│   │   │       ├── evolucao_model.py
│   │   │       ├── anexo_model.py
│   │   │       ├── log_acesso_model.py
│   │   │       └── refresh_token_model.py
│   │   ├── repositories/
│   │   │   ├── base_repository.py
│   │   │   ├── clinica_repository.py
│   │   │   ├── usuario_repository.py
│   │   │   ├── paciente_repository.py
│   │   │   ├── profissional_caso_repository.py
│   │   │   ├── protocolo_repository.py
│   │   │   ├── protocolo_paciente_repository.py
│   │   │   ├── caa_dados_repository.py
│   │   │   ├── evolucao_repository.py
│   │   │   ├── anexo_repository.py
│   │   │   ├── log_acesso_repository.py
│   │   │   └── refresh_token_repository.py
│   │   ├── storage/
│   │   │   └── minio_storage.py
│   │   ├── ai/
│   │   │   └── ai_gateway_placeholder.py
│   │   ├── auth/
│   │   │   ├── jwt_provider.py
│   │   │   └── password_hasher.py
│   │   ├── audit/
│   │   │   └── audit_logger.py
│   │   └── observability/
│   │       ├── logging.py
│   │       └── metrics.py
│   │
│   └── interface/
│       ├── dependencies.py
│       ├── middlewares/
│       │   ├── correlation_id.py
│       │   ├── rate_limit.py
│       │   └── audit.py
│       ├── schemas/
│       │   ├── auth_schema.py
│       │   ├── paciente_schema.py
│       │   ├── profissional_caso_schema.py
│       │   ├── protocolo_schema.py
│       │   ├── caa_schema.py
│       │   ├── evolucao_schema.py
│       │   └── anexo_schema.py
│       └── routers/
│           ├── auth_router.py
│           ├── pacientes_router.py
│           ├── profissionais_router.py
│           ├── protocolos_router.py
│           ├── caa_router.py
│           ├── evolucoes_router.py
│           └── anexos_router.py
│
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│
├── tests/
│   ├── unit/
│   │   ├── test_login.py
│   │   ├── test_criar_paciente.py
│   │   └── test_soft_delete.py
│   └── integration/
│       ├── test_paciente_repository.py
│       └── test_evolucao_repository.py
│
├── docs/
│   ├── arquitetura.md
│   ├── estrutura.md
│   ├── modelagem.md
│   ├── seguranca.md
│   ├── supply-chain.md
│   ├── observabilidade.md
│   ├── ia-preparacao.md
│   └── plano.md
│
├── .env
├── .env.example
├── .gitignore
├── alembic.ini
├── pyproject.toml
├── uv.lock
├── docker-compose.yml
└── CLAUDE.md
```

---

## Por que cada arquivo e pasta existe

### Raiz do projeto

**`CLAUDE.md`** — instruções para o Claude Code. Enxuto: só regras críticas e links
para os docs. Lido a cada sessão — quanto menor, mais atenção o modelo dá a cada regra.

**`pyproject.toml` + `uv.lock`** — dependências Python fixadas com hash de integridade.
Garante que qualquer ambiente (local, VPS, CI) instala exatamente o mesmo. Ver
`docs/supply-chain.md`.

**`alembic.ini`** — configuração do Alembic para migrations. Aponta para `alembic/env.py`.

**`.env`** — variáveis de ambiente reais. Nunca vai pro Git. Contém: `DATABASE_URL`,
`JWT_SECRET`, credenciais do MinIO/Redis. Cada ambiente tem o seu.

**`.env.example`** — template sem valores reais. Vai pro Git. Mostra quais variáveis
são necessárias sem expor nenhum secret.

**`docker-compose.yml`** — orquestra API + Postgres + MinIO + Redis. Ambiente local
idêntico ao de produção.

---

### `backend/`

**`main.py`** — entry point. Instancia FastAPI, registra todos os routers via
`include_router`, configura CORS, rate limiting e middlewares de observabilidade/auditoria.
Nenhuma lógica de negócio.

**`config.py`** — lê `.env` via `python-dotenv` e expõe como objeto tipado.
Centraliza toda leitura de configuração — nenhum outro arquivo chama `os.getenv()`
diretamente (exceto via config).

**`container.py`** — único arquivo que importa todas as camadas. Monta as
implementações concretas e as injeta nos use cases via FastAPI `Depends`.
Trocar banco, storage ou provedor de IA = mudar aqui, nenhum outro lugar.

---

### `domain/entities/`

Classes Python puras. Sem herança de framework. Sem decoradores externos.
Representam o que o sistema *é*.

Cada arquivo tem:
- Atributos do modelo de negócio
- Enums dos valores permitidos (`PacienteDiagnosticoStatus`, `ProtocoloStatus`,
  `EspecialidadeProfissional`, etc.)
- Métodos de negócio puro se necessário (`tem_consentimento_lgpd()`, `esta_ativo()`)

Exemplo do que **não** vai aqui: queries SQL, validação HTTP, serialização JSON.

### `domain/repositories/`

Interfaces ABC (Abstract Base Class). Definem o contrato — o que o repositório
deve fazer, sem dizer como. A `application/` depende dessas interfaces, nunca
das implementações concretas.

**`base_repository.py`** — interface genérica com métodos comuns a todos:
`salvar`, `buscar_por_id`, `listar`, `soft_delete`. Todo método que toca dado
sensível recebe `clinica_id` como parâmetro **obrigatório**, nunca opcional —
transforma "esquecer o filtro multi-tenant" em erro de tipo, não bug silencioso.

### `domain/services/`

Interfaces de serviços externos que o domínio precisa mas não controla.

**`storage_service.py`** — define `StorageServiceInterface` com `salvar`,
`obter_url` e `deletar`. O domínio não sabe se o anexo vai pro MinIO local ou
pra S3 — só chama a interface. Ver `docs/arquitetura.md`.

**`ai_gateway_service.py`** — define `AIGatewayInterface`, preparada desde já mas
sem implementação real conectada. Mesmo princípio do `storage_service.py`. Ver
`docs/ia-preparacao.md`.

### `domain/authorization/`

**`policy.py`** — política de RBAC centralizada (admin/fono/secretaria). Toda
checagem de "quem pode fazer o quê" mora aqui, não espalhada em `if` nos routers.
Ver `docs/seguranca.md`.

---

### `application/dtos/`

Dataclasses Python puras. Sem Pydantic, sem SQLAlchemy, sem HTTP.
São o "idioma" interno entre domain, application e infrastructure.

### `application/use_cases/`

Um arquivo por operação. Cada use case:
1. Recebe dependências via construtor (repositório, storage, política de autorização)
2. Executa uma única responsabilidade
3. Retorna um DTO

`CriarEvolucaoUseCase` só cria evolução. Se isso precisar disparar um evento de
domínio, isso é orquestrado pelo use case chamando o publisher — não vira lógica
solta no router.

---

### `infrastructure/database/connection.py`

Engine SQLAlchemy async e session factory. Único lugar que sabe a `DATABASE_URL`.

### `infrastructure/database/models/`

Modelos ORM — representação das tabelas para o SQLAlchemy. Diferentes das
entidades de domínio: `PacienteModel` sabe de colunas, FKs e índices; `Paciente`
(domain) sabe de regras de negócio.

**`base.py`** — Mixin com campos comuns a todas as tabelas:
`id` (UUID), `clinica_id`, `criado_em`, `atualizado_em`, `deletado`, `deletado_em`.

### `infrastructure/repositories/`

Implementações concretas das interfaces de `domain/repositories/`. Todo acesso
ao banco passa por aqui — nunca direto em use case ou router.

### `infrastructure/storage/`

**`minio_storage.py`** — implementa `StorageServiceInterface` salvando no MinIO.
Retorna `storage_ref` no formato `minio://{bucket}/{key}`.

### `infrastructure/ai/`

**`ai_gateway_placeholder.py`** — esqueleto da implementação futura de IA
(hoje só levanta `NotImplementedError`). Existe agora pra que, quando chegar a
hora, só precise preencher os métodos — não criar do zero. Ver `docs/ia-preparacao.md`.

### `infrastructure/auth/`

**`jwt_provider.py`** — geração e validação de access/refresh token.
**`password_hasher.py`** — hash argon2id, nunca vaza pra `domain/`.

### `infrastructure/audit/`

**`audit_logger.py`** — grava em `logs_acesso` toda leitura/escrita de dado
clínico sensível. Chamado pelo middleware `interface/middlewares/audit.py`.

### `infrastructure/observability/`

**`logging.py`** — configuração do `structlog` (JSON, correlation ID).
**`metrics.py`** — exposição de métricas Prometheus (`/metrics`).

---

### `interface/dependencies.py`

FastAPI `Depends` que injetam sessão de banco, usuário autenticado (valida JWT)
e a política de autorização aplicável ao caso de uso.

### `interface/middlewares/`

**`correlation_id.py`** — gera/propaga ID único por requisição.
**`rate_limit.py`** — limite de tentativas de login via Redis.
**`audit.py`** — dispara `AuditLogger` em endpoints marcados como sensíveis.

### `interface/schemas/`

Pydantic models — formato das requisições e respostas HTTP.
Cada entidade tem pelo menos três schemas: `XxxCreate`, `XxxUpdate`, `XxxResponse`.

### `interface/routers/`

Endpoints FastAPI. Responsabilidade única: adaptar HTTP para use case e vice-versa.
Sem lógica de negócio. Sem acesso direto ao banco.

---

### `alembic/versions/`

Migrations geradas automaticamente. Nunca editar o banco manualmente em produção.

### `tests/unit/`

Sem banco. Sem servidor. Testam domain e application com repositórios mock.
Devem rodar em milissegundos.

### `tests/integration/`

Com banco PostgreSQL real (banco de teste separado). Testam se os repositórios
de infrastructure funcionam corretamente contra o banco real.

### `docs/`

Documentação de referência. O `CLAUDE.md` principal referencia esses arquivos.
Lidos sob demanda — não consomem contexto desnecessariamente.
