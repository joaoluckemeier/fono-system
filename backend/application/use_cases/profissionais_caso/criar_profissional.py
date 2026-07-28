from datetime import UTC, datetime
from uuid import UUID, uuid4

from backend.application.dtos.profissional_caso_dto import (
    CriarProfissionalCasoInputDTO,
    ProfissionalCasoDTO,
    profissional_caso_to_dto,
)
from backend.application.exceptions import RecursoNaoEncontradoError
from backend.domain.entities.profissional_caso import EspecialidadeProfissional, ProfissionalCaso
from backend.domain.repositories.paciente_repository import PacienteRepository
from backend.domain.repositories.profissional_caso_repository import ProfissionalCasoRepository


class CriarProfissionalUseCase:
    def __init__(
        self,
        profissional_repository: ProfissionalCasoRepository,
        paciente_repository: PacienteRepository,
    ) -> None:
        self._profissional_repository = profissional_repository
        self._paciente_repository = paciente_repository

    async def executar(
        self, paciente_id: UUID, dto: CriarProfissionalCasoInputDTO, clinica_id: UUID
    ) -> ProfissionalCasoDTO:
        paciente = await self._paciente_repository.buscar_por_id(paciente_id, clinica_id)
        if paciente is None:
            raise RecursoNaoEncontradoError("Paciente nao encontrado")

        agora = datetime.now(UTC)
        profissional = ProfissionalCaso(
            id=uuid4(),
            clinica_id=clinica_id,
            criado_em=agora,
            atualizado_em=agora,
            deletado=False,
            deletado_em=None,
            paciente_id=paciente_id,
            nome=dto.nome,
            especialidade=EspecialidadeProfissional(dto.especialidade),
            contato=dto.contato,
        )
        salvo = await self._profissional_repository.salvar(profissional)
        return profissional_caso_to_dto(salvo)