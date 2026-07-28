from datetime import UTC, datetime
from uuid import UUID, uuid4

from backend.application.dtos.protocolo_paciente_dto import (
    CriarProtocoloPacienteInputDTO,
    ProtocoloPacienteDTO,
    protocolo_paciente_to_dto,
)
from backend.application.exceptions import RecursoNaoEncontradoError
from backend.domain.entities.protocolo_paciente import ProtocoloPaciente, StatusProtocoloPaciente
from backend.domain.repositories.paciente_repository import PacienteRepository
from backend.domain.repositories.protocolo_paciente_repository import ProtocoloPacienteRepository
from backend.domain.repositories.protocolo_repository import ProtocoloRepository


class AssociarProtocoloPacienteUseCase:
    def __init__(
        self,
        protocolo_paciente_repository: ProtocoloPacienteRepository,
        paciente_repository: PacienteRepository,
        protocolo_repository: ProtocoloRepository,
    ) -> None:
        self._protocolo_paciente_repository = protocolo_paciente_repository
        self._paciente_repository = paciente_repository
        self._protocolo_repository = protocolo_repository

    async def executar(
        self, paciente_id: UUID, dto: CriarProtocoloPacienteInputDTO, clinica_id: UUID
    ) -> ProtocoloPacienteDTO:
        paciente = await self._paciente_repository.buscar_por_id(paciente_id, clinica_id)
        if paciente is None:
            raise RecursoNaoEncontradoError("Paciente nao encontrado")

        protocolo = await self._protocolo_repository.buscar_por_id(dto.protocolo_id, clinica_id)
        if protocolo is None:
            raise RecursoNaoEncontradoError("Protocolo nao encontrado")

        status = StatusProtocoloPaciente(dto.status)
        if status is StatusProtocoloPaciente.REALIZADO and dto.data_realizacao is None:
            raise ValueError("data_realizacao e obrigatoria quando status='realizado'")

        agora = datetime.now(UTC)
        protocolo_paciente = ProtocoloPaciente(
            id=uuid4(),
            clinica_id=clinica_id,
            criado_em=agora,
            atualizado_em=agora,
            deletado=False,
            deletado_em=None,
            paciente_id=paciente_id,
            protocolo_id=dto.protocolo_id,
            status=status,
            data_realizacao=dto.data_realizacao,
            observacao=dto.observacao,
        )
        salvo = await self._protocolo_paciente_repository.salvar(protocolo_paciente)
        return protocolo_paciente_to_dto(salvo)
