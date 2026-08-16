from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class TermoGerarRequest(BaseModel):
    modelo_id: UUID


class TermoGeradoResponse(BaseModel):
    id: UUID
    clinica_id: UUID
    paciente_id: UUID
    modelo_id: UUID
    anexo_id: UUID
    gerado_por: UUID
    criado_em: datetime
    atualizado_em: datetime
