from datetime import UTC, datetime
from uuid import UUID, uuid4

from backend.application.dtos.tarefa_dto import CriarTarefaInputDTO, TarefaDTO, tarefa_to_dto
from backend.application.exceptions import PermissaoNegadaError, RecursoNaoEncontradoError
from backend.domain.authorization.policy import Recurso, usuario_pode
from backend.domain.entities.tarefa import PrioridadeTarefa, Tarefa
from backend.domain.entities.usuario import PapelUsuario
from backend.domain.repositories.paciente_repository import PacienteRepository
from backend.domain.repositories.tarefa_repository import TarefaRepository


class CriarTarefaUseCase:
    def __init__(
        self,
        tarefa_repository: TarefaRepository,
        paciente_repository: PacienteRepository,
    ) -> None:
        self._tarefa_repository = tarefa_repository
        self._paciente_repository = paciente_repository

    async def executar(
        self,
        paciente_id: UUID,
        dto: CriarTarefaInputDTO,
        clinica_id: UUID,
        papel: PapelUsuario,
    ) -> TarefaDTO:
        if not usuario_pode(papel, Recurso.PLANEJAMENTO_TERAPEUTICO):
            raise PermissaoNegadaError("Papel sem permissao para criar tarefa de planejamento")

        paciente = await self._paciente_repository.buscar_por_id(paciente_id, clinica_id)
        if paciente is None:
            raise RecursoNaoEncontradoError("Paciente nao encontrado")

        agora = datetime.now(UTC)
        tarefa = Tarefa(
            id=uuid4(),
            clinica_id=clinica_id,
            criado_em=agora,
            atualizado_em=agora,
            deletado=False,
            deletado_em=None,
            paciente_id=paciente_id,
            data=dto.data,
            titulo=dto.titulo,
            descricao=dto.descricao,
            prioridade=PrioridadeTarefa(dto.prioridade),
        )
        salvo = await self._tarefa_repository.salvar(tarefa)
        return tarefa_to_dto(salvo)
