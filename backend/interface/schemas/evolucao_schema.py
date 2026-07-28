from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class EvolucaoCreate(BaseModel):
    data: date
    texto: str


class ConfirmarEvolucaoRequest(BaseModel):
    texto_final: str | None = None


class EvolucaoResponse(BaseModel):
    id: UUID
    clinica_id: UUID
    paciente_id: UUID
    usuario_id: UUID
    data: date
    texto: str
    status: str
    criado_em: datetime
    atualizado_em: datetime
