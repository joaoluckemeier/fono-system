from uuid import UUID

from backend.application.exceptions import PermissaoNegadaError, RecursoNaoEncontradoError
from backend.domain.authorization.policy import Recurso, usuario_pode
from backend.domain.entities.usuario import PapelUsuario
from backend.domain.repositories.tarefa_repository import TarefaRepository


class DeletarTarefaUseCase:
    def __init__(self, tarefa_repository: TarefaRepository) -> None:
        self._tarefa_repository = tarefa_repository

    async def executar(self, id: UUID, clinica_id: UUID, papel: PapelUsuario) -> None:
        if not usuario_pode(papel, Recurso.PLANEJAMENTO_TERAPEUTICO):
            raise PermissaoNegadaError("Papel sem permissao para excluir tarefa de planejamento")

        tarefa = await self._tarefa_repository.buscar_por_id(id, clinica_id)
        if tarefa is None:
            raise RecursoNaoEncontradoError("Tarefa nao encontrada")

        await self._tarefa_repository.soft_delete(id, clinica_id)
