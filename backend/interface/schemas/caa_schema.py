from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CaaUpdate(BaseModel):
    usa_caa: bool
    protocolo_aip_aplicado: bool
    sistema_ajustado: bool
    observacoes: str | None = None


class CaaResponse(BaseModel):
    id: UUID
    clinica_id: UUID
    paciente_id: UUID
    usa_caa: bool
    protocolo_aip_aplicado: bool
    sistema_ajustado: bool
    observacoes: str | None
    criado_em: datetime
    atualizado_em: datetime
