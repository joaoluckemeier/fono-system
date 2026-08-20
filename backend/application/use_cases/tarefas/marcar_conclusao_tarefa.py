from datetime import UTC, datetime
from uuid import UUID

from backend.application.dtos.tarefa_dto import TarefaDTO, tarefa_to_dto
from backend.application.exceptions import PermissaoNegadaError, RecursoNaoEncontradoError
from backend.domain.authorization.policy import Recurso, usuario_pode
from backend.domain.entities.usuario import PapelUsuario
from backend.domain.repositories.tarefa_repository import TarefaRepository


class MarcarConclusaoTarefaUseCase:
    """Toggle dedicado do checkbox - acao de alta frequencia disparada direto
    da lista, sem precisar reenviar o card inteiro (ver AtualizarTarefaUseCase)."""

    def __init__(self, tarefa_repository: TarefaRepository) -> None:
        self._tarefa_repository = tarefa_repository

    async def executar(
        self,
        id: UUID,
        concluido: bool,
        clinica_id: UUID,
        papel: PapelUsuario,
    ) -> TarefaDTO:
        if not usuario_pode(papel, Recurso.PLANEJAMENTO_TERAPEUTICO):
            raise PermissaoNegadaError("Papel sem permissao para concluir tarefa de planejamento")

        tarefa = await self._tarefa_repository.buscar_por_id(id, clinica_id)
        if tarefa is None:
            raise RecursoNaoEncontradoError("Tarefa nao encontrada")

        tarefa.concluido = concluido
        tarefa.concluido_em = datetime.now(UTC) if concluido else None

        salvo = await self._tarefa_repository.salvar(tarefa)
        return tarefa_to_dto(salvo)
