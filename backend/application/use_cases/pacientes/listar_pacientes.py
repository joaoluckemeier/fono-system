from uuid import UUID

from backend.application.dtos.paciente_dto import PacienteDTO, paciente_to_dto
from backend.domain.repositories.paciente_repository import PacienteRepository


class ListarPacientesUseCase:
    def __init__(self, paciente_repository: PacienteRepository) -> None:
        self._paciente_repository = paciente_repository

    async def executar(self, clinica_id: UUID) -> list[PacienteDTO]:
        pacientes = await self._paciente_repository.listar(clinica_id)
        return [paciente_to_dto(p) for p in pacientes]
