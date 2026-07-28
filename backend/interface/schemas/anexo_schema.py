from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AnexoResponse(BaseModel):
    id: UUID
    clinica_id: UUID
    entidade_tipo: str
    entidade_id: UUID
    tipo_arquivo: str
    nome_arquivo: str
    storage_ref: str
    criado_por: UUID
    criado_em: datetime
    atualizado_em: datetime
