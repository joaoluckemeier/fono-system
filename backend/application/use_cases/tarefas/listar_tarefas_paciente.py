from datetime import date
from uuid import UUID

from backend.application.dtos.tarefa_dto import TarefaDTO, tarefa_to_dto
from backend.application.exceptions import PermissaoNegadaError
from backend.domain.authorization.policy import Recurso, usuario_pode
from backend.domain.entities.usuario import PapelUsuario
from backend.domain.repositories.tarefa_repository import TarefaRepository


class ListarTarefasPacienteUseCase:
    def __init__(self, tarefa_repository: TarefaRepository) -> None:
        self._tarefa_repository = tarefa_repository

    async def executar(
        self,
        paciente_id: UUID,
        clinica_id: UUID,
        papel: PapelUsuario,
        data_inicio: date | None = None,
        data_fim: date | None = None,
    ) -> list[TarefaDTO]:
        if not usuario_pode(papel, Recurso.PLANEJAMENTO_TERAPEUTICO):
            raise PermissaoNegadaError("Papel sem permissao para ver tarefas de planejamento")

        if data_inicio is not None and data_fim is not None:
            tarefas = await self._tarefa_repository.listar_por_paciente_periodo(
                paciente_id, clinica_id, data_inicio, data_fim
            )
        else:
            tarefas = [
                t
                for t in await self._tarefa_repository.listar(clinica_id)
                if t.paciente_id == paciente_id
            ]
        return [tarefa_to_dto(t) for t in tarefas]
