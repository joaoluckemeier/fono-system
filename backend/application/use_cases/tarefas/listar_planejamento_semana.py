from datetime import date
from uuid import UUID

from backend.application.dtos.tarefa_dto import TarefasPorPacienteDTO, tarefa_to_dto
from backend.application.exceptions import PermissaoNegadaError
from backend.domain.authorization.policy import Recurso, usuario_pode
from backend.domain.entities.usuario import PapelUsuario
from backend.domain.repositories.paciente_repository import PacienteRepository
from backend.domain.repositories.tarefa_repository import TarefaRepository


class ListarPlanejamentoSemanaUseCase:
    """Visao agregada cross-paciente: um 'card' por paciente com suas tarefas
    no periodo, pra comecar a semana sabendo o que esta em aberto sem abrir
    paciente por paciente. Pacientes sem nenhuma tarefa no periodo nao aparecem."""

    def __init__(
        self,
        tarefa_repository: TarefaRepository,
        paciente_repository: PacienteRepository,
    ) -> None:
        self._tarefa_repository = tarefa_repository
        self._paciente_repository = paciente_repository

    async def executar(
        self,
        clinica_id: UUID,
        papel: PapelUsuario,
        data_inicio: date,
        data_fim: date,
    ) -> list[TarefasPorPacienteDTO]:
        if not usuario_pode(papel, Recurso.PLANEJAMENTO_TERAPEUTICO):
            raise PermissaoNegadaError("Papel sem permissao para ver planejamento semanal")

        tarefas = await self._tarefa_repository.listar_por_periodo(clinica_id, data_inicio, data_fim)

        por_paciente: dict[UUID, list] = {}
        for tarefa in tarefas:
            por_paciente.setdefault(tarefa.paciente_id, []).append(tarefa)

        cards: list[TarefasPorPacienteDTO] = []
        for paciente_id, tarefas_paciente in por_paciente.items():
            paciente = await self._paciente_repository.buscar_por_id(paciente_id, clinica_id)
            nome = paciente.nome_completo if paciente is not None else "Paciente"
            cards.append(
                TarefasPorPacienteDTO(
                    paciente_id=paciente_id,
                    paciente_nome=nome,
                    tarefas=[tarefa_to_dto(t) for t in tarefas_paciente],
                )
            )
        return cards
