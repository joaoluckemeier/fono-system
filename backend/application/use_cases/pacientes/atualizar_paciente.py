from uuid import UUID

from backend.application.dtos.paciente_dto import AtualizarPacienteInputDTO, PacienteDTO, paciente_to_dto
from backend.application.exceptions import PermissaoNegadaError, RecursoNaoEncontradoError
from backend.domain.authorization.policy import Recurso, usuario_pode
from backend.domain.entities.usuario import PapelUsuario
from backend.domain.repositories.paciente_repository import PacienteRepository


class AtualizarPacienteUseCase:
    def __init__(self, paciente_repository: PacienteRepository) -> None:
        self._paciente_repository = paciente_repository

    async def executar(
        self,
        id: UUID,
        dto: AtualizarPacienteInputDTO,
        clinica_id: UUID,
        papel: PapelUsuario,
    ) -> PacienteDTO:
        if not usuario_pode(papel, Recurso.PACIENTE_CADASTRO):
            raise PermissaoNegadaError("Papel sem permissao para editar paciente")

        paciente = await self._paciente_repository.buscar_por_id(id, clinica_id)
        if paciente is None:
            raise RecursoNaoEncontradoError("Paciente nao encontrado")

        paciente.nome_completo = dto.nome_completo
        paciente.data_nascimento = dto.data_nascimento
        paciente.nome_mae = dto.nome_mae
        paciente.nome_pai = dto.nome_pai
        paciente.tem_irmaos = dto.tem_irmaos
        paciente.faz_uso_medicamento = dto.faz_uso_medicamento
        paciente.nome_irmaos = dto.nome_irmaos
        paciente.diagnostico = dto.diagnostico
        paciente.data_inicio_nipwin = dto.data_inicio_nipwin
        paciente.consentimento_lgpd_assinado_em = dto.consentimento_lgpd_assinado_em

        salvo = await self._paciente_repository.salvar(paciente)
        return paciente_to_dto(salvo)
