from uuid import UUID

from backend.application.exceptions import RecursoNaoEncontradoError
from backend.domain.repositories.protocolo_paciente_repository import ProtocoloPacienteRepository


class DeletarProtocoloPacienteUseCase:
    """Remove a associacao de um protocolo com um paciente (ex: adicionado por engano).
    Nao afeta o catalogo de protocolos em si."""

    def __init__(self, protocolo_paciente_repository: ProtocoloPacienteRepository) -> None:
        self._protocolo_paciente_repository = protocolo_paciente_repository

    async def executar(self, id: UUID, clinica_id: UUID) -> None:
        registro = await self._protocolo_paciente_repository.buscar_por_id(id, clinica_id)
        if registro is None:
            raise RecursoNaoEncontradoError("Protocolo do paciente nao encontrado")

        await self._protocolo_paciente_repository.soft_delete(id, clinica_id)
