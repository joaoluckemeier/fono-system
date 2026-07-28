from uuid import UUID

from backend.application.exceptions import RecursoNaoEncontradoError
from backend.domain.repositories.profissional_caso_repository import ProfissionalCasoRepository


class DeletarProfissionalUseCase:
    def __init__(self, profissional_repository: ProfissionalCasoRepository) -> None:
        self._profissional_repository = profissional_repository

    async def executar(self, id: UUID, clinica_id: UUID) -> None:
        profissional = await self._profissional_repository.buscar_por_id(id, clinica_id)
        if profissional is None:
            raise RecursoNaoEncontradoError("Profissional nao encontrado")
        await self._profissional_repository.soft_delete(id, clinica_id)
