from abc import abstractmethod
from uuid import UUID

from backend.domain.entities.termo_gerado import TermoGerado
from backend.domain.repositories.base_repository import BaseRepository


class TermoGeradoRepository(BaseRepository[TermoGerado]):
    @abstractmethod
    async def listar_por_paciente(self, paciente_id: UUID, clinica_id: UUID) -> list[TermoGerado]: ...
