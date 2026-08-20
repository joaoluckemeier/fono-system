from abc import abstractmethod
from datetime import date
from uuid import UUID

from backend.domain.entities.tarefa import Tarefa
from backend.domain.repositories.base_repository import BaseRepository


class TarefaRepository(BaseRepository[Tarefa]):
    @abstractmethod
    async def listar_por_paciente_periodo(
        self, paciente_id: UUID, clinica_id: UUID, data_inicio: date, data_fim: date
    ) -> list[Tarefa]: ...

    @abstractmethod
    async def listar_por_periodo(
        self, clinica_id: UUID, data_inicio: date, data_fim: date
    ) -> list[Tarefa]: ...
