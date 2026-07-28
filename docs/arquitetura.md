# Arquitetura — Fono System

## Por que Clean Architecture

O sistema guarda dados sensíveis de saúde de criança (diagnóstico, medicação,
evolução clínica) e precisa crescer sem reescritas: trocar PostgreSQL por outro
banco, trocar MinIO por S3, ativar multi-tenant real pra outras clínicas,
plugar IA no fluxo de evolução. Clean Architecture garante que cada uma dessas
mudanças toca exatamente uma camada — sem efeito cascata.

---

## As quatro camadas em detalhe

### `domain/` — núcleo puro

Zero dependências externas. Importa apenas stdlib Python.

Contém:
- **Entidades** — classes Python puras com atributos e regras de negócio intrínsecas.
  `Paciente` sabe o que é um paciente em acompanhamento fonoaudiológico. Não sabe
  de banco, HTTP ou arquivo.
- **Interfaces de repositório** — classes ABC que definem *o que* o repositório
  faz, sem dizer *como*. `application/` depende dessas interfaces, nunca das
  implementações.
- **Interfaces de serviço** — contratos para serviços externos
  (`StorageServiceInterface`, `AIGatewayInterface`).
- **Política de autorização** — RBAC centralizado, consumido por `application/`.

Pode ser testado completamente sem banco, sem servidor, sem nada externo.

### `application/` — casos de uso

Importa apenas `domain/`. Um arquivo por operação de negócio.

Contém:
- **Use cases** — `CriarPacienteUseCase`, `RegistrarEvolucaoUseCase`, etc.
  Recebem dependências via construtor (repositório, storage, política de
  autorização). Executam uma coisa só. Se `RegistrarEvolucao` precisar disparar
  um evento de domínio, isso é orquestrado aqui — não vai pro router.
- **DTOs** — dataclasses Python puras para transferência entre camadas internas.
  Sem Pydantic. Sem SQLAlchemy. Sem HTTP.

### `infrastructure/` — implementações concretas

Importa apenas `domain/`. Implementa as interfaces definidas lá.

Contém:
- **Modelos ORM** — `PacienteModel` com colunas, FKs e índices para o SQLAlchemy.
  Diferente da entidade `Paciente` (domain): um sabe de banco, o outro sabe de negócio.
- **Repositórios concretos** — implementam `PacienteRepositoryInterface` usando
  SQLAlchemy. Todo acesso ao banco passa por aqui.
- **Storage concreto** — `MinIOStorageService`.
- **Auth concreto** — `JWTProvider`, hash argon2id.
- **Auditoria concreta** — `AuditLogger`, grava `logs_acesso`.
- **Observabilidade concreta** — logging estruturado, métricas Prometheus.
- **IA (esqueleto)** — `AIGatewayPlaceholder`, ver `docs/ia-preparacao.md`.

### `interface/` — adaptadores HTTP

Importa `application/` via container. Nunca acessa `infrastructure/` diretamente.

Contém:
- **Schemas Pydantic** — formato das requisições e respostas HTTP.
  Cada entidade tem: `XxxCreate`, `XxxUpdate`, `XxxResponse`.
- **Routers FastAPI** — recebem request, convertem schema em DTO, chamam use
  case, convertem DTO de volta em schema, devolvem. Sem lógica de negócio.
- **Middlewares** — correlation ID, rate limiting, auditoria automática.
- **dependencies.py** — FastAPI `Depends` para sessão de banco e usuário autenticado.

---

## `container.py` — o único lugar que conhece tudo

`backend/container.py` é o único arquivo com permissão de importar todas as camadas.
É a "cola" do sistema — monta as dependências concretas e injeta nos use cases.

```
container.py
  └── importa PacienteRepositoryImpl   (infra) — implementa PacienteRepositoryInterface (domain)
  └── importa MinIOStorageService      (infra) — implementa StorageServiceInterface (domain)
  └── monta   CriarPacienteUseCase(repository=PacienteRepositoryImpl, storage=MinIOStorageService)
  └── expõe   use case pronto via FastAPI Depends
  └── router  recebe o use case — sem saber o que está por baixo
```

**Trocar PostgreSQL por outro banco** = trocar implementação do repositório em
`container.py`. Nenhuma outra camada toca.

**Trocar MinIO por S3** = trocar `MinIOStorageService` por `S3StorageService`
em `container.py`. Nenhuma outra camada toca.

**Conectar a primeira feature de IA de verdade** = implementar
`RealAIGatewayService` e trocar `AIGatewayPlaceholder` por ela em `container.py`
(mais a variável `AI_GATEWAY_MODO=real` no `.env`). Nenhuma outra camada muda.
Ver `docs/ia-preparacao.md`.

---

## DTOs vs Schemas — distinção crítica

### `application/dtos/` — transferência interna entre camadas

```python
# dataclass Python pura — sem Pydantic, sem HTTP
from dataclasses import dataclass
from datetime import date
from uuid import UUID

@dataclass
class PacienteDTO:
    id: UUID
    clinica_id: UUID
    nome_completo: str
    data_nascimento: date
    diagnostico: str
```

Usado entre domain, application e infrastructure. Não conhece HTTP.

### `interface/schemas/` — transferência HTTP entre API e cliente

```python
# Pydantic model — validação de request/response HTTP
from pydantic import BaseModel
from datetime import date

class PacienteCreate(BaseModel):
    nome_completo: str
    data_nascimento: date
    diagnostico: str

class PacienteResponse(BaseModel):
    id: UUID
    nome_completo: str
    diagnostico: str
    criado_em: datetime
```

Usado apenas na camada de interface. Não conhece domínio diretamente.

### Fluxo completo

```
HTTP request
  → Router recebe body como PacienteCreate (schema Pydantic)
  → Router converte para PacienteDTO
  → Router chama CriarPacienteUseCase(dto)
  → UseCase valida autorização via domain/authorization/policy.py
  → UseCase chama repository.salvar(dto)
  → Repository persiste, retorna PacienteDTO
  → Router converte PacienteDTO para PacienteResponse (schema Pydantic)
  → HTTP response
```

---

## Enums — onde os valores são validados

Campos como `especialidade`, `status` de protocolo e `tipo_arquivo` de anexo são
`VARCHAR` no banco (sem enum PostgreSQL). A validação dos valores permitidos
acontece no domínio, via enum Python puro:

```python
# domain/entities/profissional_caso.py
from enum import Enum

class EspecialidadeProfissional(Enum):
    NUTRICIONISTA = "nutricionista"
    FISIOTERAPEUTA = "fisioterapeuta"
    PSICOLOGO = "psicologo"
    TERAPEUTA_OCUPACIONAL = "terapeuta_ocupacional"
    ATENDENTE_TERAPEUTICA = "atendente_terapeutica"
    PEDIATRA = "pediatra"
    NEUROPEDIATRA = "neuropediatra"
    PSIQUIATRA = "psiquiatra"
    OUTRO = "outro"
```

O banco aceita qualquer string — o domínio rejeita valores inválidos antes de
persistir. Evita lock-in de enum no PostgreSQL (`ALTER TYPE` é caro em produção)
e mantém a validação onde deve estar: no negócio, não na infraestrutura.

---

## Multi-tenant

Toda tabela sensível tem `clinica_id`. Toda query filtra por `clinica_id`.

- **Hoje:** a clínica da Beta, `clinica_id` carregado no JWT.
- **Futuro:** cada usuário carrega seu `clinica_id` no token — nenhuma query muda.
- **Adicionar clínica nova:** inserir linha em `clinicas` + criar `usuarios` vinculados.

O design multi-tenant está embutido desde o dia 1 porque essa é a diferença entre
"sistema pessoal da Beta" e "produto pra outras fonoaudiólogas" — ativar o segundo
uso é só uma questão de onboarding, não de reescrita de schema.

**Estratégia escolhida — isolamento lógico via coluna, não schema/banco separado:**

| Estratégia | Isolamento | Complexidade operacional | Quando migrar pra ela |
|---|---|---|---|
| `clinica_id` em cada linha (escolhida) | Lógico | Baixa — um único banco, um único deploy | Fase de validação, poucas dezenas de clínicas |
| Schema separado por clínica | Forte | Média — migrations rodam N vezes | Se contrato exigir isolamento formal |
| Banco separado por clínica | Máximo | Alta — cada clínica é um deploy próprio | Só sob exigência regulatória forte |

---

## Referência cruzada

- Tabelas concretas: `docs/modelagem.md`
- Autorização (RBAC) e auditoria: `docs/seguranca.md`
- Onde o `AIGatewayInterface` se encaixa: `docs/ia-preparacao.md`
- Observabilidade (logging, métricas): `docs/observabilidade.md`
