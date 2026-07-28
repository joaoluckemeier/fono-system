from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class ProtocoloCreate(BaseModel):
    nome: str
    descricao: str | None = None


class ProtocoloResponse(BaseModel):
    id: UUID
    clinica_id: UUID
    nome: str
    descricao: str | None
    criado_em: datetime
    atualizado_em: datetime


class ProtocoloPacienteCreate(BaseModel):
    protocolo_id: UUID
    status: str
    data_realizacao: date | None = None
    observacao: str | None = None


class ProtocoloPacienteStatusUpdate(BaseModel):
    status: str
    data_realizacao: date | None = None


class ProtocoloPacienteResponse(BaseModel):
    id: UUID
    clinica_id: UUID
    paciente_id: UUID
    protocolo_id: UUID
    status: str
    data_realizacao: date | None
    observacao: str | None
    criado_em: datetime
    atualizado_em: datetime
