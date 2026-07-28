from uuid import UUID

from backend.application.dtos.profissional_caso_dto import ProfissionalCasoDTO, profissional_caso_to_dto
from backend.domain.repositories.profissional_caso_repository import ProfissionalCasoRepository


class ListarProfissionaisUseCase:
    def __init__(self, profissional_repository: ProfissionalCasoRepository) -> None:
        self._profissional_repository = profissional_repository

    async def executar(self, paciente_id: UUID, clinica_id: UUID) -> list[ProfissionalCasoDTO]:
        profissionais = await self._profissional_repository.listar_por_paciente(
            paciente_id, clinica_id
        )
        return [profissional_caso_to_dto(p) for p in profissionais]
