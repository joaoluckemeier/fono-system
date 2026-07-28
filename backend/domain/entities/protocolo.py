from dataclasses import dataclass

from backend.domain.entities.base import EntidadeBase


@dataclass
class Protocolo(EntidadeBase):
    nome: str
    descricao: str | None = None
