from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID


class PlanoClinica(Enum):
    BASICO = "basico"
    PRO = "pro"


@dataclass
class Clinica:
    """Tabela raiz do sistema. Nao herda EntidadeBase: nao tem clinica_id nem soft delete."""

    id: UUID
    nome: str
    plano: PlanoClinica
    criado_em: datetime
