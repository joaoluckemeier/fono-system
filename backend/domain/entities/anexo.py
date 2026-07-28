from dataclasses import dataclass
from enum import Enum
from uuid import UUID

from backend.domain.entities.base import EntidadeBase


class EntidadeAnexavel(Enum):
    PACIENTE = "paciente"
    EVOLUCAO = "evolucao"
    PROTOCOLO_PACIENTE = "protocolo_paciente"


class TipoArquivo(Enum):
    PDF = "pdf"
    FOTO = "foto"
    AUDIO = "audio"
    VIDEO = "video"
    OUTRO = "outro"


@dataclass
class Anexo(EntidadeBase):
    entidade_tipo: EntidadeAnexavel
    entidade_id: UUID
    tipo_arquivo: TipoArquivo
    nome_arquivo: str
    storage_ref: str
    criado_por: UUID
