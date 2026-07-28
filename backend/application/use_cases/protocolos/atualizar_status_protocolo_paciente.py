from uuid import UUID

from backend.application.dtos.protocolo_paciente_dto import (
    AtualizarStatusProtocoloPacienteInputDTO,
    ProtocoloPacienteDTO,
    protocolo_paciente_to_dto,
)
from backend.application.exceptions import RecursoNaoEncontradoError
from backend.domain.entities.protocolo_paciente import StatusProtocoloPaciente
from backend.domain.repositories.protocolo_paciente_repository import ProtocoloPacienteRepository


class AtualizarStatusProtocoloPacienteUseCase:
    def __init__(self, protocolo_paciente_repository: ProtocoloPacienteRepository) -> None:
        self._protocolo_paciente_repository = protocolo_paciente_repository

    async def executar(
        self, id: UUID, dto: AtualizarStatusProtocoloPacienteInputDTO, clinica_id: UUID
    ) -> ProtocoloPacienteDTO:
        registro = await self._protocolo_paciente_repository.buscar_por_id(id, clinica_id)
        if registro is None:
            raise RecursoNaoEncontradoError("Protocolo do paciente nao encontrado")

        novo_status = StatusProtocoloPaciente(dto.status)
        data_realizacao = dto.data_realizacao or registro.data_realizacao
        if novo_status is StatusProtocoloPaciente.REALIZADO and data_realizacao is None:
            raise ValueError("data_realizacao e obrigatoria quando status='realizado'")

        registro.status = novo_status
        registro.data_realizacao = data_realizacao
        salvo = await self._protocolo_paciente_repository.salvar(registro)
        return protocolo_paciente_to_dto(salvo)
