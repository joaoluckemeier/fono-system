from uuid import UUID

from backend.application.dtos.tarefa_dto import AtualizarTarefaInputDTO, TarefaDTO, tarefa_to_dto
from backend.application.exceptions import PermissaoNegadaError, RecursoNaoEncontradoError
from backend.domain.authorization.policy import Recurso, usuario_pode
from backend.domain.entities.tarefa import PrioridadeTarefa
from backend.domain.entities.usuario import PapelUsuario
from backend.domain.repositories.tarefa_repository import TarefaRepository


class AtualizarTarefaUseCase:
    def __init__(self, tarefa_repository: TarefaRepository) -> None:
        self._tarefa_repository = tarefa_repository

    async def executar(
        self,
        id: UUID,
        dto: AtualizarTarefaInputDTO,
        clinica_id: UUID,
        papel: PapelUsuario,
    ) -> TarefaDTO:
        if not usuario_pode(papel, Recurso.PLANEJAMENTO_TERAPEUTICO):
            raise PermissaoNegadaError("Papel sem permissao para editar tarefa de planejamento")

        tarefa = await self._tarefa_repository.buscar_por_id(id, clinica_id)
        if tarefa is None:
            raise RecursoNaoEncontradoError("Tarefa nao encontrada")

        tarefa.data = dto.data
        tarefa.titulo = dto.titulo
        tarefa.descricao = dto.descricao
        tarefa.prioridade = PrioridadeTarefa(dto.prioridade)

        salvo = await self._tarefa_repository.salvar(tarefa)
        return tarefa_to_dto(salvo)
