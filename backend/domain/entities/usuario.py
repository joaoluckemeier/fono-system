from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from backend.domain.entities.base import EntidadeBase


class PapelUsuario(Enum):
    ADMIN = "admin"
    FONO = "fono"
    SECRETARIA = "secretaria"


@dataclass
class Usuario(EntidadeBase):
    email: str
    senha_hash: str
    nome: str
    papel: PapelUsuario
    ativo: bool
    ultimo_login_em: datetime | None = None
