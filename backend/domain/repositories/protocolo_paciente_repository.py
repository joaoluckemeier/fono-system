from abc import abstractmethod
from uuid import UUID

from backend.domain.entities.protocolo_paciente import ProtocoloPaciente
from backend.domain.repositories.base_repository import BaseRepository


class ProtocoloPacienteRepository(BaseRepository[ProtocoloPaciente]):
    @abstractmethod
    async def listar_por_paciente(
        self, paciente_id: UUID, clinica_id: UUID
    ) -> list[ProtocoloPaciente]: ...
