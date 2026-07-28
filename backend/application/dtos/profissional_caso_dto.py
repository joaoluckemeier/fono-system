from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from backend.domain.entities.profissional_caso import ProfissionalCaso


@dataclass
class CriarProfissionalCasoInputDTO:
    nome: str
    especialidade: str
    contato: str | None = None


@dataclass
class ProfissionalCasoDTO:
    id: UUID
    clinica_id: UUID
    paciente_id: UUID
    nome: str
    especialidade: str
    contato: str | None
    criado_em: datetime
    atualizado_em: datetime


def profissional_caso_to_dto(profissional: ProfissionalCaso) -> ProfissionalCasoDTO:
    return ProfissionalCasoDTO(
        id=profissional.id,
        clinica_id=profissional.clinica_id,
        paciente_id=profissional.paciente_id,
        nome=profissional.nome,
        especialidade=profissional.especialidade.value,
        contato=profissional.contato,
        criado_em=profissional.criado_em,
        atualizado_em=profissional.atualizado_em,
    )
