from datetime import UTC, datetime
from uuid import UUID, uuid4

from backend.application.dtos.protocolo_dto import CriarProtocoloInputDTO, ProtocoloDTO, protocolo_to_dto
from backend.domain.entities.protocolo import Protocolo
from backend.domain.repositories.protocolo_repository import ProtocoloRepository


class CriarProtocoloUseCase:
    def __init__(self, protocolo_repository: ProtocoloRepository) -> None:
        self._protocolo_repository = protocolo_repository

    async def executar(self, dto: CriarProtocoloInputDTO, clinica_id: UUID) -> ProtocoloDTO:
        agora = datetime.now(UTC)
        protocolo = Protocolo(
            id=uuid4(),
            clinica_id=clinica_id,
            criado_em=agora,
            atualizado_em=agora,
            deletado=False,
            deletado_em=None,
            nome=dto.nome,
            descricao=dto.descricao,
        )
        salvo = await self._protocolo_repository.salvar(protocolo)
        return protocolo_to_dto(salvo)
