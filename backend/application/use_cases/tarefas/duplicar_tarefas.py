from datetime import UTC, datetime
from uuid import UUID, uuid4

from backend.application.dtos.tarefa_dto import DuplicarTarefasInputDTO, TarefaDTO, tarefa_to_dto
from backend.application.exceptions import PermissaoNegadaError, RecursoNaoEncontradoError
from backend.domain.authorization.policy import Recurso, usuario_pode
from backend.domain.entities.tarefa import Tarefa
from backend.domain.entities.usuario import PapelUsuario
from backend.domain.repositories.tarefa_repository import TarefaRepository


class DuplicarTarefasUseCase:
    """Duplicacao manual/seletiva: a fono escolhe tarefas de um periodo anterior
    e cria copias resetadas (nao concluidas) numa nova data. Nao ha motor de
    recorrencia automatica."""

    def __init__(self, tarefa_repository: TarefaRepository) -> None:
        self._tarefa_repository = tarefa_repository

    async def executar(
        self,
        paciente_id: UUID,
        dto: DuplicarTarefasInputDTO,
        clinica_id: UUID,
        papel: PapelUsuario,
    ) -> list[TarefaDTO]:
        if not usuario_pode(papel, Recurso.PLANEJAMENTO_TERAPEUTICO):
            raise PermissaoNegadaError("Papel sem permissao para duplicar tarefa de planejamento")

        copias: list[Tarefa] = []
        for tarefa_id in dto.tarefa_ids:
            origem = await self._tarefa_repository.buscar_por_id(tarefa_id, clinica_id)
            if origem is None or origem.paciente_id != paciente_id:
                raise RecursoNaoEncontradoError("Tarefa nao encontrada")

            agora = datetime.now(UTC)
            copia = Tarefa(
                id=uuid4(),
                clinica_id=clinica_id,
                criado_em=agora,
                atualizado_em=agora,
                deletado=False,
                deletado_em=None,
                paciente_id=paciente_id,
                data=dto.nova_data,
                titulo=origem.titulo,
                descricao=origem.descricao,
                prioridade=origem.prioridade,
                concluido=False,
                concluido_em=None,
            )
            copias.append(await self._tarefa_repository.salvar(copia))

        return [tarefa_to_dto(t) for t in copias]
