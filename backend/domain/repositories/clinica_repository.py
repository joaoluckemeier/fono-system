from abc import ABC, abstractmethod
from uuid import UUID

from backend.domain.entities.clinica import Clinica


class ClinicaRepository(ABC):
    """Clinica e a tabela raiz - nao tem clinica_id proprio, por isso nao usa BaseRepository."""

    @abstractmethod
    async def salvar(self, clinica: Clinica) -> Clinica: ...

    @abstractmethod
    async def buscar_por_id(self, id: UUID) -> Clinica | None: ...

    @abstractmethod
    async def listar(self) -> list[Clinica]: ...
