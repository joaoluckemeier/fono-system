# Modelagem do banco — Fono System

## Campos comuns em todas as tabelas (via `base.py`)

```python
id            UUID        PK, default uuid4
clinica_id    UUID        FK → clinicas.id, NOT NULL
criado_em     TIMESTAMP   default now()
atualizado_em TIMESTAMP   default now(), on update now()
deletado      BOOLEAN     default False
deletado_em   TIMESTAMP   nullable
```

`deletado` e `deletado_em` implementam soft delete. Toda query filtra
`deletado == False`. Registros deletados ficam no banco para auditoria —
relevante para um prontuário clínico, que não pode simplesmente desaparecer.

`clinica_id` em toda tabela (não só nas raiz) garante que o filtro de segurança
multi-tenant é sempre direto — sem JOIN extra para verificar a qual clínica um
registro pertence.

---

## Tabelas

### clinicas
Clínica/fonoaudióloga cliente do sistema. Hoje sempre um único registro (a Beta).
Futuro: cada fonoaudióloga é uma clínica separada.

| Campo | Tipo | Obs |
|---|---|---|
| id | UUID | PK |
| nome | VARCHAR | Nome da clínica |
| plano | VARCHAR | 'basico', 'pro' |
| criado_em | TIMESTAMP | |

> `clinicas` não herda o Mixin base — não tem `clinica_id` nem soft delete.
> É a tabela raiz do sistema.

---

### usuarios
Usuário autenticado vinculado a uma clínica.

| Campo | Tipo | Obs |
|---|---|---|
| id | UUID | PK |
| clinica_id | UUID | FK → clinicas |
| email | VARCHAR | unique por clínica |
| senha_hash | VARCHAR | argon2id — nunca texto puro |
| nome | VARCHAR | |
| papel | VARCHAR | 'admin', 'fono', 'secretaria' |
| ativo | BOOLEAN | default true |
| ultimo_login_em | TIMESTAMP | nullable |

> `email` é unique por clínica, não globalmente. Duas clínicas diferentes podem
> ter o mesmo email — são sistemas isolados. `papel` é validado via enum Python
> no domínio (ver `docs/arquitetura.md` → seção Enums) e consumido pela política
> de RBAC em `docs/seguranca.md`.

---

### pacientes
Criança em acompanhamento fonoaudiológico. Entidade central — evoluções,
protocolos, CAA e anexos se ligam diretamente ao paciente.

| Campo | Tipo | Obs |
|---|---|---|
| id | UUID | PK |
| clinica_id | UUID | FK → clinicas |
| nome_completo | VARCHAR | |
| data_nascimento | DATE | |
| nome_mae | VARCHAR | |
| nome_pai | VARCHAR | |
| tem_irmaos | BOOLEAN | |
| nome_irmaos | TEXT | nullable |
| diagnostico | TEXT | texto livre na v1 — ver decisão abaixo |
| data_inicio | DATE | |
| faz_uso_medicamento | TEXT | |
| consentimento_lgpd_assinado_em | TIMESTAMP | nullable — rastreabilidade, não substitui o documento jurídico |
| informacoes_nascimento | TEXT | nullable — texto livre |
| queixa_principal | TEXT | nullable — queixa principal da família |
| observacoes | TEXT | nullable — campo aberto |

> `idade` não é uma coluna — é calculada em tempo de leitura a partir de `data_nascimento`
> (`Paciente.idade` em `domain/entities/paciente.py`), para nunca dessincronizar do dado real.

---

### profissionais_caso
Profissional externo envolvido no caso (nutri, fisio, psico...). Cadastro
informativo — sem login no sistema.

| Campo | Tipo | Obs |
|---|---|---|
| id | UUID | PK |
| clinica_id | UUID | FK → clinicas |
| paciente_id | UUID | FK → pacientes |
| nome | VARCHAR | |
| especialidade | VARCHAR | enum no domínio — ver `docs/arquitetura.md` |
| contato | VARCHAR | nullable |

---

### protocolos
Catálogo de protocolos fonoaudiológicos por clínica (ex: ABFW). Editável pela
fonoaudióloga — não é lista fixa do sistema.

| Campo | Tipo | Obs |
|---|---|---|
| id | UUID | PK |
| clinica_id | UUID | FK → clinicas |
| nome | VARCHAR | |
| descricao | TEXT | nullable |

---

### protocolos_paciente
Protocolo aplicado ou planejado para um paciente específico.

| Campo | Tipo | Obs |
|---|---|---|
| id | UUID | PK |
| paciente_id | UUID | FK → pacientes |
| protocolo_id | UUID | FK → protocolos |
| status | VARCHAR | 'realizado', 'planejado' |
| data_realizacao | DATE | nullable, obrigatório se status='realizado' |
| observacao | TEXT | nullable |

---

### caa_dados
Dados de Comunicação Aumentativa e Alternativa do paciente. Relação 1:1.

| Campo | Tipo | Obs |
|---|---|---|
| id | UUID | PK |
| paciente_id | UUID | FK → pacientes, unique |
| usa_caa | BOOLEAN | |
| protocolo_aip_aplicado | BOOLEAN | |
| sistema_ajustado | BOOLEAN | |
| observacoes | TEXT | nullable |

---

### evolucoes
Timeline de atendimentos do paciente. Separado do paciente pra permitir
histórico completo, ordenação e auditoria de leitura — a "última devolutiva"
nunca é um campo próprio, é sempre a evolução mais recente desta tabela.

| Campo | Tipo | Obs |
|---|---|---|
| id | UUID | PK |
| clinica_id | UUID | FK → clinicas |
| paciente_id | UUID | FK → pacientes |
| usuario_id | UUID | FK → usuarios, quem registrou |
| data | DATE | |
| texto | TEXT | |

---

### tarefas_planejamento
Planejamento terapêutico semanal — checklist de tarefas soltas atreladas a um
paciente, com data de referência (não existe um objeto "semana" separado; a
semana é só um filtro de consulta por intervalo de datas). Conclusão é um
checkbox simples, estilo Todoist, sem estados intermediários. Duplicação de
tarefas de uma semana pra outra é manual/seletiva — sem motor de recorrência
automática.

| Campo | Tipo | Obs |
|---|---|---|
| id | UUID | PK |
| clinica_id | UUID | FK → clinicas |
| paciente_id | UUID | FK → pacientes |
| data | DATE | data de referência da tarefa (dá o dia da semana) |
| titulo | VARCHAR | |
| descricao | TEXT | nullable |
| prioridade | VARCHAR | 'alta', 'media', 'baixa' |
| concluido | BOOLEAN | default false |
| concluido_em | TIMESTAMP | nullable, preenchido ao marcar concluído |

---

### anexos
Arquivo associado a paciente, evolução ou protocolo aplicado. Polimórfico —
Aberto/Fechado (OCP): novos tipos de entidade anexável não exigem alteração de
schema. O banco guarda apenas `storage_ref`, resolvido pelo `StorageService`.

| Campo | Tipo | Obs |
|---|---|---|
| id | UUID | PK |
| clinica_id | UUID | FK → clinicas |
| entidade_tipo | VARCHAR | 'paciente', 'evolucao', 'protocolo_paciente' — extensível |
| entidade_id | UUID | |
| tipo_arquivo | VARCHAR | 'pdf', 'foto', 'audio', 'video', 'outro' |
| nome_arquivo | VARCHAR | nome amigável do arquivo |
| storage_ref | VARCHAR | referência opaca → resolvida pelo StorageService |
| criado_por | UUID | FK → usuarios |

> `storage_ref` tem formato `minio://{bucket}/{key}`. Quando migrar para S3, o
> formato muda para `s3://{bucket}/{key}`. O banco não sabe a diferença.

---

### modelos_termo
Catálogo de modelos de termo/encaminhamento pré-cadastrados pela clínica, com
placeholders (`{{nome_paciente}}`, `{{idade}}`, etc.) mesclados na hora da geração.

| Campo | Tipo | Obs |
|---|---|---|
| id | UUID | PK |
| clinica_id | UUID | FK → clinicas |
| nome | VARCHAR | |
| tipo | VARCHAR | 'termo', 'encaminhamento' |
| corpo_texto | TEXT | com placeholders |
| ativo | BOOLEAN | default true — desativado some da seleção mas não é soft delete |

---

### termos_gerados
Log de rastreabilidade de cada termo/encaminhamento efetivamente gerado para um
paciente — liga o modelo usado ao PDF salvo em `anexos`. `criado_em` (herdado)
já é a data de geração, não há coluna separada para isso.

| Campo | Tipo | Obs |
|---|---|---|
| id | UUID | PK |
| clinica_id | UUID | FK → clinicas |
| paciente_id | UUID | FK → pacientes |
| modelo_id | UUID | FK → modelos_termo |
| anexo_id | UUID | FK → anexos, o PDF gerado |
| gerado_por | UUID | FK → usuarios |

---

### logs_acesso
Auditoria — não só escrita, também **leitura** de dado clínico sensível.

| Campo | Tipo | Obs |
|---|---|---|
| id | UUID | PK |
| clinica_id | UUID | FK → clinicas |
| usuario_id | UUID | FK → usuarios |
| acao | VARCHAR | 'visualizar', 'criar', 'editar', 'excluir', 'exportar' |
| entidade_tipo | VARCHAR | 'paciente', 'evolucao', 'anexo'... |
| entidade_id | UUID | |
| ip_origem | VARCHAR | |

---

### refresh_tokens
Permite revogar sessão antes da expiração do JWT — um JWT puro não pode ser
"cancelado" antes do timestamp de expiração.

| Campo | Tipo | Obs |
|---|---|---|
| id | UUID | PK |
| usuario_id | UUID | FK → usuarios |
| token_hash | VARCHAR | hash do refresh token, nunca texto puro |
| expira_em | TIMESTAMP | |
| revogado | BOOLEAN | default false |

---

## Diagrama de relacionamentos

```
clinicas
  ├── usuarios (clinica_id)
  ├── pacientes (clinica_id)
  │     ├── profissionais_caso (paciente_id)
  │     ├── protocolos_paciente (paciente_id)
  │     │     └── protocolos (protocolo_id, catálogo por clínica)
  │     ├── caa_dados (paciente_id, 1:1)
  │     ├── evolucoes (paciente_id)
  │     │     └── usuarios (usuario_id, quem registrou)
  │     ├── anexos (entidade_id → paciente | evolucao | protocolo_paciente)
  │     ├── tarefas_planejamento (paciente_id)
  │     └── termos_gerados (paciente_id)
  │           ├── modelos_termo (modelo_id, catálogo por clínica)
  │           └── anexos (anexo_id, o PDF gerado)
  ├── modelos_termo (clinica_id)
  ├── logs_acesso (clinica_id)
  └── usuarios
        └── refresh_tokens (usuario_id)
```

---

## Decisões de modelagem

**UUID em vez de integer sequencial** — IDs inteiros são previsíveis e enumeráveis.
Um atacante que sabe que `/pacientes/3` existe pode tentar `/pacientes/4`. UUID
não é enumerável. Também facilita multi-tenant: duas clínicas podem criar
registros simultaneamente sem conflito de ID.

**`evolucoes` como histórico e não um campo fixo "última devolutiva"** — sempre
`SELECT * FROM evolucoes WHERE paciente_id = X ORDER BY data DESC LIMIT 1`. Dá
histórico completo, auditoria de quem registrou o quê, e nunca perde informação
por sobrescrita.

**`protocolos` como catálogo por clínica, não texto livre** — decisão mantida
em aberto até validação com a Beta (ver `docs/plano.md`), mas o catálogo é a
opção mais segura de começar: é mais fácil simplificar pra texto livre depois
do que o contrário, e habilita relatório futuro tipo "quantos pacientes usam
o Protocolo X".

**`diagnostico` como texto livre** — decisão consciente de simplicidade na v1,
com espaço pra evoluir pra catálogo estruturado (CID) depois, sem quebrar nada.

**`anexos` polimórfico em vez de uma tabela por tipo** — evita `foto_paciente`,
`pdf_protocolo`, `audio_avaliacao` como tabelas separadas. Aplica o princípio
Aberto/Fechado: anexar a uma entidade nova é usar a tabela que já existe, não
alterar schema.

**Soft delete em vez de hard delete** — prontuário clínico não pode simplesmente
ser apagado. Soft delete garante auditoria sem complexidade de banco:
`deletado = True`, `deletado_em = now()`. A query padrão filtra
`deletado == False` automaticamente.

**`storage_ref` em vez de `url` ou `data_url`** — referência opaca que o
`StorageService` resolve. Nem o banco nem o domínio precisam saber onde o
arquivo está guardado fisicamente. É o DIP aplicado ao storage.
