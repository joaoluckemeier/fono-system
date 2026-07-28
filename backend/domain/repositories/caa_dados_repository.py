from abc import abstractmethod
from uuid import UUID

from backend.domain.entities.caa_dados import CaaDados
from backend.domain.repositories.base_repository import BaseRepository


class CaaDadosRepository(BaseRepository[CaaDados]):
    @abstractmethod
    async def buscar_por_paciente(self, paciente_id: UUID, clinica_id: UUID) -> CaaDados | None: ...
