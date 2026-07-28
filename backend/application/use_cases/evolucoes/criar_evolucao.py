from datetime import UTC, datetime
from uuid import UUID, uuid4

from backend.application.dtos.evolucao_dto import CriarEvolucaoInputDTO, EvolucaoDTO, evolucao_to_dto
from backend.application.exceptions import PermissaoNegadaError, RecursoNaoEncontradoError
from backend.domain.authorization.policy import Recurso, usuario_pode
from backend.domain.entities.evolucao import Evolucao
from backend.domain.entities.usuario import PapelUsuario
from backend.domain.repositories.evolucao_repository import EvolucaoRepository
from backend.domain.repositories.paciente_repository import PacienteRepository


class CriarEvolucaoUseCase:
    def __init__(
        self,
        evolucao_repository: EvolucaoRepository,
        paciente_repository: PacienteRepository,
    ) -> None:
        self._evolucao_repository = evolucao_repository
        self._paciente_repository = paciente_repository

    async def executar(
        self,
        paciente_id: UUID,
        dto: CriarEvolucaoInputDTO,
        clinica_id: UUID,
        usuario_id: UUID,
        papel: PapelUsuario,
    ) -> EvolucaoDTO:
        if not usuario_pode(papel, Recurso.EVOLUCAO):
            raise PermissaoNegadaError("Papel sem permissao para registrar evolucao clinica")

        paciente = await self._paciente_repository.buscar_por_id(paciente_id, clinica_id)
        if paciente is None:
            raise RecursoNaoEncontradoError("Paciente nao encontrado")

        agora = datetime.now(UTC)
        evolucao = Evolucao(
            id=uuid4(),
            clinica_id=clinica_id,
            criado_em=agora,
            atualizado_em=agora,
            deletado=False,
            deletado_em=None,
            paciente_id=paciente_id,
            usuario_id=usuario_id,
            data=dto.data,
            texto=dto.texto,
        )
        salvo = await self._evolucao_repository.salvar(evolucao)
        return evolucao_to_dto(salvo)
