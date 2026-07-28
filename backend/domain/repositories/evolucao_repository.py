from abc import abstractmethod
from uuid import UUID

from backend.domain.entities.evolucao import Evolucao
from backend.domain.repositories.base_repository import BaseRepository


class EvolucaoRepository(BaseRepository[Evolucao]):
    @abstractmethod
    async def listar_por_paciente(self, paciente_id: UUID, clinica_id: UUID) -> list[Evolucao]: ...

    @abstractmethod
    async def buscar_ultima(self, paciente_id: UUID, clinica_id: UUID) -> Evolucao | None: ...
