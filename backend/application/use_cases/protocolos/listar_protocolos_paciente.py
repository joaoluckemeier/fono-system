from uuid import UUID

from backend.application.dtos.protocolo_paciente_dto import (
    ProtocoloPacienteDTO,
    protocolo_paciente_to_dto,
)
from backend.domain.repositories.protocolo_paciente_repository import ProtocoloPacienteRepository


class ListarProtocolosPacienteUseCase:
    def __init__(self, protocolo_paciente_repository: ProtocoloPacienteRepository) -> None:
        self._protocolo_paciente_repository = protocolo_paciente_repository

    async def executar(self, paciente_id: UUID, clinica_id: UUID) -> list[ProtocoloPacienteDTO]:
        registros = await self._protocolo_paciente_repository.listar_por_paciente(
            paciente_id, clinica_id
        )
        return [protocolo_paciente_to_dto(r) for r in registros]
