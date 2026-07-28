from dataclasses import dataclass
from uuid import UUID

from backend.domain.entities.base import EntidadeBase


@dataclass
class CaaDados(EntidadeBase):
    paciente_id: UUID
    usa_caa: bool
    protocolo_aip_aplicado: bool
    sistema_ajustado: bool
    observacoes: str | None = None
