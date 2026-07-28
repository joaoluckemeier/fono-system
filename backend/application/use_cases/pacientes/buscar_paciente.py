from uuid import UUID

from backend.application.dtos.paciente_dto import PacienteDTO, paciente_to_dto
from backend.application.exceptions import RecursoNaoEncontradoError
from backend.domain.repositories.paciente_repository import PacienteRepository


class BuscarPacienteUseCase:
    def __init__(self, paciente_repository: PacienteRepository) -> None:
        self._paciente_repository = paciente_repository

    async def executar(self, id: UUID, clinica_id: UUID) -> PacienteDTO:
        paciente = await self._paciente_repository.buscar_por_id(id, clinica_id)
        if paciente is None:
            raise RecursoNaoEncontradoError("Paciente nao encontrado")
        return paciente_to_dto(paciente)
