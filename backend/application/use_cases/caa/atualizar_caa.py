from datetime import UTC, datetime
from uuid import UUID, uuid4

from backend.application.dtos.caa_dados_dto import AtualizarCaaInputDTO, CaaDadosDTO, caa_dados_to_dto
from backend.application.exceptions import PermissaoNegadaError, RecursoNaoEncontradoError
from backend.domain.authorization.policy import Recurso, usuario_pode
from backend.domain.entities.caa_dados import CaaDados
from backend.domain.entities.usuario import PapelUsuario
from backend.domain.repositories.caa_dados_repository import CaaDadosRepository
from backend.domain.repositories.paciente_repository import PacienteRepository


class AtualizarCaaUseCase:
    def __init__(
        self,
        caa_dados_repository: CaaDadosRepository,
        paciente_repository: PacienteRepository,
    ) -> None:
        self._caa_dados_repository = caa_dados_repository
        self._paciente_repository = paciente_repository

    async def executar(
        self,
        paciente_id: UUID,
        dto: AtualizarCaaInputDTO,
        clinica_id: UUID,
        papel: PapelUsuario,
    ) -> CaaDadosDTO:
        if not usuario_pode(papel, Recurso.PACIENTE_CLINICO):
            raise PermissaoNegadaError("Papel sem permissao para editar dados de CAA")

        paciente = await self._paciente_repository.buscar_por_id(paciente_id, clinica_id)
        if paciente is None:
            raise RecursoNaoEncontradoError("Paciente nao encontrado")

        existente = await self._caa_dados_repository.buscar_por_paciente(paciente_id, clinica_id)
        agora = datetime.now(UTC)

        if existente is None:
            caa = CaaDados(
                id=uuid4(),
                clinica_id=clinica_id,
                criado_em=agora,
                atualizado_em=agora,
                deletado=False,
                deletado_em=None,
                paciente_id=paciente_id,
                usa_caa=dto.usa_caa,
                protocolo_aip_aplicado=dto.protocolo_aip_aplicado,
                sistema_ajustado=dto.sistema_ajustado,
                observacoes=dto.observacoes,
            )
        else:
            caa = existente
            caa.usa_caa = dto.usa_caa
            caa.protocolo_aip_aplicado = dto.protocolo_aip_aplicado
            caa.sistema_ajustado = dto.sistema_ajustado
            caa.observacoes = dto.observacoes

        salvo = await self._caa_dados_repository.salvar(caa)
        return caa_dados_to_dto(salvo)
