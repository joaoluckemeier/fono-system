from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class PacienteCreate(BaseModel):
    nome_completo: str
    data_nascimento: date
    nome_mae: str
    nome_pai: str
    tem_irmaos: bool
    faz_uso_medicamento: str
    nome_irmaos: str | None = None
    diagnostico: str | None = None
    data_inicio: date | None = None
    consentimento_lgpd_assinado_em: datetime | None = None
    informacoes_nascimento: str | None = None
    queixa_principal: str | None = None
    observacoes: str | None = None


class PacienteUpdate(PacienteCreate):
    pass


class PacienteStatusUpdate(BaseModel):
    status: str


class PacienteResponseCadastral(BaseModel):
    """Visao sem dados clinicos sensiveis - usada quando o papel e secretaria."""

    id: UUID
    clinica_id: UUID
    nome_completo: str
    data_nascimento: date
    nome_mae: str
    nome_pai: str
    tem_irmaos: bool
    status: str
    nome_irmaos: str | None
    consentimento_lgpd_assinado_em: datetime | None
    idade: int
    observacoes: str | None
    criado_em: datetime
    atualizado_em: datetime


class PacienteResponse(PacienteResponseCadastral):
    """Visao completa - admin/fono, inclui diagnostico e dados clinicos."""

    diagnostico: str | None
    data_inicio: date | None
    faz_uso_medicamento: str
    informacoes_nascimento: str | None
    queixa_principal: str | None
