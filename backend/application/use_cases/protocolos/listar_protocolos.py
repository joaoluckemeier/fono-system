from uuid import UUID

from backend.application.dtos.protocolo_dto import ProtocoloDTO, protocolo_to_dto
from backend.domain.repositories.protocolo_repository import ProtocoloRepository


class ListarProtocolosUseCase:
    def __init__(self, protocolo_repository: ProtocoloRepository) -> None:
        self._protocolo_repository = protocolo_repository

    async def executar(self, clinica_id: UUID) -> list[ProtocoloDTO]:
        protocolos = await self._protocolo_repository.listar(clinica_id)
        return [protocolo_to_dto(p) for p in protocolos]
