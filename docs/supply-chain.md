# Supply chain — Fono System

Dependência de terceiros é, na prática, código de terceiros rodando com o
mesmo acesso que o seu — inclusive ao banco com dado clínico. Tratamento
explícito, não só "pip install e segue".

---

## Gerenciador de dependências e lockfile

`uv` (mantido pela Astral, mesma equipe do `ruff`) com lockfile (`uv.lock`)
commitado no repositório.

```bash
uv add fastapi
uv add --dev pytest pip-audit
uv sync   # instala exatamente o que está no lockfile
```

**Por que o lockfile é inegociável:** sem ele, `pip install fastapi` pode
trazer versões diferentes em cada máquina/deploy — porta pra dependência
maliciosa nova entrar sem ninguém perceber. Com lockfile, toda instalação usa
exatamente as mesmas versões, com hash de integridade verificado.

**Alternativa considerada:** Poetry — mais maduro, mas sensivelmente mais
lento em resolução de dependências e no build da imagem Docker.

---

## Scan de vulnerabilidades conhecidas

`pip-audit` (mantida pela Python Packaging Authority, cruza dependências com
a base OSV/PyPA) rodando no CI a cada push/PR.

```bash
uv run pip-audit
```

Build falha se aparecer vulnerabilidade de severidade alta/crítica sem
exceção justificada. Vulnerabilidade baixa/média vira issue rastreada, não
bloqueia automaticamente.

`Trivy` escaneia a imagem Docker final — não só as dependências Python, mas o
SO base e libs de sistema. Ponto que costuma passar batido: time audita
`pyproject.toml` mas ignora que `python:3.12` carrega pacotes de sistema com
CVEs conhecidas.

---

## Atualização de dependências

Dependabot (nativo do GitHub, gratuito) abrindo PR automático quando uma
dependência tem atualização de segurança. PR passa pelos mesmos pre-commit
hooks + CI (testes + pip-audit) antes de merge — nunca merge automático em
dependência que toca produção.

---

## Reduzindo superfície de ataque

- **Imagem base mínima**: `python:3.12-slim`, não a imagem completa.
- **Container roda como usuário não-root**: se uma dependência for
  comprometida, o dano fica limitado ao que aquele usuário pode fazer dentro
  do container.
- **Cuidado com typosquatting**: ao adicionar dependência nova fora do básico,
  confirmar nome exato, número de downloads e mantenedor antes de instalar.

```dockerfile
FROM python:3.12-slim
RUN useradd --create-home appuser
WORKDIR /app
COPY pyproject.toml uv.lock .
RUN uv sync --frozen --no-dev
COPY . .
USER appuser
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## SBOM — item de fase futura

Gerar SBOM (`cyclonedx-bom`) lista exatamente quais componentes e versões
compõem o sistema num dado momento — útil se um dia precisar responder
auditoria ou pergunta de clínica-cliente sobre vulnerabilidades. Não bloqueante
pra v1, barato de automatizar no CI quando o resto estiver estável.

---

## Referência cruzada

- Fase do roadmap em que isso entra (Fase 0): `docs/plano.md`
- Stack protegida por essas práticas: `docs/arquitetura.md`
