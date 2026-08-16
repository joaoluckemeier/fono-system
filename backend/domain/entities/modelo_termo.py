from dataclasses import dataclass
from enum import Enum

from backend.domain.entities.base import EntidadeBase


class TipoModeloTermo(Enum):
    TERMO = "termo"
    ENCAMINHAMENTO = "encaminhamento"


@dataclass
class ModeloTermo(EntidadeBase):
    nome: str
    tipo: TipoModeloTermo
    corpo_texto: str
    ativo: bool = True
