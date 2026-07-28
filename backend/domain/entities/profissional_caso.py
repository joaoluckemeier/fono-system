from dataclasses import dataclass
from enum import Enum
from uuid import UUID

from backend.domain.entities.base import EntidadeBase


class EspecialidadeProfissional(Enum):
    NUTRICIONISTA = "nutricionista"
    FISIOTERAPEUTA = "fisioterapeuta"
    PSICOLOGO = "psicologo"
    TERAPEUTA_OCUPACIONAL = "terapeuta_ocupacional"
    ATENDENTE_TERAPEUTICA = "atendente_terapeutica"
    PEDIATRA = "pediatra"
    NEUROPEDIATRA = "neuropediatra"
    PSIQUIATRA = "psiquiatra"
    OUTRO = "outro"


@dataclass
class ProfissionalCaso(EntidadeBase):
    paciente_id: UUID
    nome: str
    especialidade: EspecialidadeProfissional
    contato: str | None = None
