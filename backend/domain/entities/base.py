from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class EntidadeBase:
    """Campos comuns a toda entidade filha de uma clinica (soft delete + multi-tenant)."""

    id: UUID
    clinica_id: UUID
    criado_em: datetime
    atualizado_em: datetime
    deletado: bool
    deletado_em: datetime | None
