from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from backend.domain.entities.base import EntidadeBase


@dataclass
class RefreshToken(EntidadeBase):
    usuario_id: UUID
    token_hash: str
    expira_em: datetime
    revogado: bool = False
