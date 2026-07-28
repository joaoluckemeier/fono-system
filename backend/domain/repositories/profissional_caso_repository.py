from abc import abstractmethod
from uuid import UUID

from backend.domain.entities.profissional_caso import ProfissionalCaso
from backend.domain.repositories.base_repository import BaseRepository


class ProfissionalCasoRepository(BaseRepository[ProfissionalCaso]):
    @abstractmethod
    async def listar_por_paciente(
        self, paciente_id: UUID, clinica_id: UUID
    ) -> list[ProfissionalCaso]: ...
