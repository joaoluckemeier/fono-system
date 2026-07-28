from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from backend.domain.entities.anexo import Anexo


@dataclass
class CriarAnexoInputDTO:
    entidade_tipo: str
    entidade_id: UUID
    tipo_arquivo: str
    nome_arquivo: str
    conteudo: bytes


@dataclass
class AnexoDTO:
    id: UUID
    clinica_id: UUID
    entidade_tipo: str
    entidade_id: UUID
    tipo_arquivo: str
    nome_arquivo: str
    storage_ref: str
    criado_por: UUID
    criado_em: datetime
    atualizado_em: datetime


def anexo_to_dto(anexo: Anexo) -> AnexoDTO:
    return AnexoDTO(
        id=anexo.id,
        clinica_id=anexo.clinica_id,
        entidade_tipo=anexo.entidade_tipo.value,
        entidade_id=anexo.entidade_id,
        tipo_arquivo=anexo.tipo_arquivo.value,
        nome_arquivo=anexo.nome_arquivo,
        storage_ref=anexo.storage_ref,
        criado_por=anexo.criado_por,
        criado_em=anexo.criado_em,
        atualizado_em=anexo.atualizado_em,
    )
