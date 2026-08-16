from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from backend.domain.entities.modelo_termo import ModeloTermo


@dataclass
class CriarModeloTermoInputDTO:
    nome: str
    tipo: str
    corpo_texto: str


@dataclass
class AtualizarModeloTermoInputDTO:
    nome: str
    tipo: str
    corpo_texto: str
    ativo: bool


@dataclass
class ModeloTermoDTO:
    id: UUID
    clinica_id: UUID
    nome: str
    tipo: str
    corpo_texto: str
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime


def modelo_termo_to_dto(modelo: ModeloTermo) -> ModeloTermoDTO:
    return ModeloTermoDTO(
        id=modelo.id,
        clinica_id=modelo.clinica_id,
        nome=modelo.nome,
        tipo=modelo.tipo.value,
        corpo_texto=modelo.corpo_texto,
        ativo=modelo.ativo,
        criado_em=modelo.criado_em,
        atualizado_em=modelo.atualizado_em,
    )
