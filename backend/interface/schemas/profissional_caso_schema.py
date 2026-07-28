from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ProfissionalCasoCreate(BaseModel):
    nome: str
    especialidade: str
    contato: str | None = None


class ProfissionalCasoResponse(BaseModel):
    id: UUID
    clinica_id: UUID
    paciente_id: UUID
    nome: str
    especialidade: str
    contato: str | None
    criado_em: datetime
    atualizado_em: datetime
