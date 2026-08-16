from dataclasses import dataclass
from uuid import UUID

from backend.domain.entities.base import EntidadeBase


@dataclass
class TermoGerado(EntidadeBase):
    paciente_id: UUID
    modelo_id: UUID
    anexo_id: UUID
    gerado_por: UUID
