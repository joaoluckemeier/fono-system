from dataclasses import dataclass
from enum import Enum
from uuid import UUID

from backend.domain.entities.base import EntidadeBase


class AcaoAuditoria(Enum):
    VISUALIZAR = "visualizar"
    CRIAR = "criar"
    EDITAR = "editar"
    EXCLUIR = "excluir"
    EXPORTAR = "exportar"


@dataclass
class LogAcesso(EntidadeBase):
    usuario_id: UUID
    acao: AcaoAuditoria
    entidade_tipo: str
    entidade_id: UUID
    ip_origem: str
