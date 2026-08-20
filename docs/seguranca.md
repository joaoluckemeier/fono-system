# Segurança — Fono System

Sistema com dados sensíveis: diagnóstico, medicação e evolução clínica de
criança. Segurança é implementada em camadas — cada fase adiciona proteção
adequada ao risco real naquele momento. Ver trade-offs em cada fase.

---

## Fase 1 — Dia 1 (obrigatório antes de qualquer uso)

### JWT de vida curta + refresh revogável

Access token válido por 15 minutos. Refresh token válido por 7-30 dias,
guardado com hash em `refresh_tokens` (nunca texto puro) — permite revogar
sessão antes da expiração, algo que um JWT puro não permite.

```python
# config.py
JWT_SECRET = os.getenv("JWT_SECRET")       # 256 bits, gerado com secrets.token_hex(32)
JWT_ALGORITHM = "HS256"
JWT_ACCESS_EXPIRATION_MINUTES = 15
JWT_REFRESH_EXPIRATION_DAYS = 30
```

Por que 15 minutos e não 8 horas: se o token vazar, a janela de exploração é
curta. O custo é mais requisições de refresh — aceitável pra dado de saúde.

### Senha com argon2id

A senha nunca é guardada em texto puro. O banco guarda apenas o hash argon2id
(mais resistente a ataque por hardware dedicado que bcrypt — recomendação atual
da OWASP). Se o banco vazar, as senhas não são legíveis.

```python
from argon2 import PasswordHasher
ph = PasswordHasher()

# ao criar usuário
senha_hash = ph.hash(senha_plain)

# ao fazer login
ph.verify(senha_hash, senha_plain)
```

### Autorização (RBAC) centralizada

Autenticação (JWT) responde "quem é você". Autorização responde "o que você
pode fazer" — fica explícito em `domain/authorization/policy.py`, nunca
espalhado em `if` soltos dentro de cada endpoint.

| Ação | admin | fono | secretaria |
|---|---|---|---|
| Cadastrar/editar paciente (dados cadastrais) | ✅ | ✅ | ✅ |
| Ver diagnóstico e dados clínicos sensíveis | ✅ | ✅ | ❌ |
| Criar/editar evolução clínica | ✅ | ✅ | ❌ |
| Ver evoluções | ✅ | ✅ | ❌ |
| Anexar arquivo | ✅ | ✅ | ✅ (não-clínico) |
| Gerenciar modelos de termo/encaminhamento | ✅ | ❌ | ❌ |
| Gerar termo/encaminhamento para um paciente | ✅ | ✅ | ❌ |
| Criar/editar/concluir tarefas de planejamento terapêutico | ✅ | ✅ | ❌ |
| Ver planejamento semanal (por paciente ou agregado) | ✅ | ✅ | ❌ |
| Gerenciar usuários da clínica | ✅ | ❌ | ❌ |
| Ver logs de auditoria | ✅ | ❌ | ❌ |

### `.env` fora do Git

`JWT_SECRET`, `DATABASE_URL`, credenciais do MinIO/Redis ficam apenas no `.env`.
`.env` está no `.gitignore`. O repositório contém apenas `.env.example` com os
nomes das variáveis, sem valores. Mesma regra vale pra qualquer credencial de
provedor de IA quando `docs/ia-preparacao.md` sair do papel.

### Rate limiting no login

Endpoint `POST /auth/login` limitado a 5 requisições por minuto por IP. Após
5 tentativas erradas consecutivas, o IP fica bloqueado por 15 minutos.
Implementado via `slowapi` + Redis.

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, ...):
    ...
```

### CORS restrito

A API só aceita requisições da origem do frontend configurado. Em
desenvolvimento: `http://localhost:5173`. Em produção: o domínio real.

### Auditoria de leitura de dado clínico

Tabela `logs_acesso` registra não só escrita, mas **leitura** de dado sensível
(visualização de prontuário/evolução) — padrão esperado em sistema de saúde.
Implementado como middleware (`interface/middlewares/audit.py`), disparado
automaticamente nos endpoints marcados como sensíveis.

---

## Fase 2 — No deploy (VPS)

### HTTPS via Let's Encrypt

Obrigatório antes de expor o sistema publicamente. Dado clínico de criança
trafegando em HTTP puro não é aceitável — risco técnico e responsabilidade
sobre dado de saúde de menor sob a LGPD.

Configurado via Certbot + Nginx. Certificado gratuito, renovação automática.

### Security headers no Nginx

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Content-Security-Policy "default-src 'self'" always;
```

### Backup automático, criptografado, fora da VPS

```bash
# cron diário às 3h
0 3 * * * pg_dump $DATABASE_URL | gpg --encrypt | gzip > /backups/fono_$(date +%Y%m%d).sql.gz.gpg
find /backups -name "*.gz.gpg" -mtime +30 -delete
```

O backup precisa ficar **fora da própria VPS** (outro storage, outro provedor) —
se a VPS for comprometida ou cair, o backup não pode estar no mesmo lugar.
Perda de prontuário não tem como ser "aceita como risco".

### Usuário PostgreSQL com permissão mínima

```sql
CREATE USER fono_app WITH PASSWORD '...';
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO fono_app;
```

A aplicação não pode dropar tabelas, criar schemas ou alterar estrutura.
Protege contra dano acidental e limita impacto de uma invasão.

### Disco criptografado (LUKS)

Baseline de criptografia em repouso. Criptografia por coluna (ex: só
`diagnostico` criptografado no banco) é upgrade possível — trade-off real:
dificulta busca/filtro nesses campos. Fica como item de Fase 3, não bloqueante.

---

## Fase 3 — Pode esperar (baixo risco no contexto atual)

### Criptografia por coluna nos campos mais sensíveis

Só entra se houver exigência contratual específica de clínicas maiores que
adotarem o sistema como produto.

### Limite de payload

Limitar tamanho máximo de cada requisição (ex: 5MB, considerando anexo de
áudio/vídeo). Ajustar quando o volume real de uso de anexos for conhecido.

### Detecção de anomalia e alertas

Monitorar padrões suspeitos: muitas tentativas de login, acessos em horários
incomuns, volume anormal de requisições por `clinica_id`. Complexidade
operacional alta, valor baixo enquanto o sistema tem poucas clínicas. Implementar
quando o número de clínicas crescer.

### Sanitização de HTML

Relevante quando o sistema renderizar input do usuário como HTML (ex: editor
rich-text nas evoluções). Hoje o campo `texto` é exibido como texto puro —
baixo risco.

---

## LGPD e consentimento

Campo `consentimento_lgpd_assinado_em` no cadastro do paciente dá
rastreabilidade, mas **não substitui** o documento jurídico de consentimento
assinado pelos responsáveis — isso é processo, fora do escopo técnico. Dado
de criança + diagnóstico + medicação é o nível de cuidado mais alto entre
todas as categorias de dado que a LGPD cobre.

---

## O que nunca mudar

Independente de fase ou contexto:

- `eval()` ou `exec()` com input externo — nunca
- SQL raw concatenado com string de usuário — nunca (SQLAlchemy resolve)
- Secrets no código ou no Git — nunca
- Senha em texto puro no banco — nunca
- HTTPS opcional em produção — nunca (dado de saúde de menor)
- Texto gerado por IA persistido como evolução oficial sem revisão humana —
  nunca, ver `docs/ia-preparacao.md`

---

## Referência cruzada

- Tabelas envolvidas (`logs_acesso`, `refresh_tokens`, `pacientes`): `docs/modelagem.md`
- Segurança da cadeia de dependências (complementar): `docs/supply-chain.md`
- Onde `auth/` e `audit/` vivem na estrutura: `docs/arquitetura.md`
