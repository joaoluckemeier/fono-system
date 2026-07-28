from datetime import UTC, datetime
from uuid import UUID, uuid4

from backend.application.dtos.paciente_dto import CriarPacienteInputDTO, PacienteDTO, paciente_to_dto
from backend.application.exceptions import PermissaoNegadaError
from backend.domain.authorization.policy import Recurso, usuario_pode
from backend.domain.entities.paciente import Paciente
from backend.domain.entities.usuario import PapelUsuario
from backend.domain.repositories.paciente_repository import PacienteRepository


class CriarPacienteUseCase:
    def __init__(self, paciente_repository: PacienteRepository) -> None:
        self._paciente_repository = paciente_repository

    async def executar(
        self, dto: CriarPacienteInputDTO, clinica_id: UUID, papel: PapelUsuario
    ) -> PacienteDTO:
        if not usuario_pode(papel, Recurso.PACIENTE_CADASTRO):
            raise PermissaoNegadaError("Papel sem permissao para cadastrar paciente")

        agora = datetime.now(UTC)
        paciente = Paciente(
            id=uuid4(),
            clinica_id=clinica_id,
            criado_em=agora,
            atualizado_em=agora,
            deletado=False,
            deletado_em=None,
            nome_completo=dto.nome_completo,
            data_nascimento=dto.data_nascimento,
            nome_mae=dto.nome_mae,
            nome_pai=dto.nome_pai,
            tem_irmaos=dto.tem_irmaos,
            faz_uso_medicamento=dto.faz_uso_medicamento,
            nome_irmaos=dto.nome_irmaos,
            diagnostico=dto.diagnostico,
            data_inicio_nipwin=dto.data_inicio_nipwin,
            consentimento_lgpd_assinado_em=dto.consentimento_lgpd_assinado_em,
        )
        salvo = await self._paciente_repository.salvar(paciente)
        return paciente_to_dto(salvo)
