from datetime import UTC, datetime
from uuid import UUID, uuid4

from backend.application.dtos.anexo_dto import AnexoDTO, CriarAnexoInputDTO, anexo_to_dto
from backend.application.exceptions import PermissaoNegadaError
from backend.domain.authorization.policy import Recurso, usuario_pode
from backend.domain.entities.anexo import Anexo, EntidadeAnexavel, TipoArquivo
from backend.domain.entities.usuario import PapelUsuario
from backend.domain.repositories.anexo_repository import AnexoRepository
from backend.domain.services.storage_service import StorageServiceInterface

_RECURSO_POR_ENTIDADE = {
    EntidadeAnexavel.EVOLUCAO: Recurso.ANEXO_CLINICO,
    EntidadeAnexavel.PACIENTE: Recurso.ANEXO_NAO_CLINICO,
    EntidadeAnexavel.PROTOCOLO_PACIENTE: Recurso.ANEXO_NAO_CLINICO,
}


class CriarAnexoUseCase:
    def __init__(
        self, anexo_repository: AnexoRepository, storage_service: StorageServiceInterface
    ) -> None:
        self._anexo_repository = anexo_repository
        self._storage_service = storage_service

    async def executar(
        self,
        dto: CriarAnexoInputDTO,
        clinica_id: UUID,
        criado_por: UUID,
        papel: PapelUsuario,
    ) -> AnexoDTO:
        entidade_tipo = EntidadeAnexavel(dto.entidade_tipo)
        recurso = _RECURSO_POR_ENTIDADE[entidade_tipo]
        if not usuario_pode(papel, recurso):
            raise PermissaoNegadaError("Papel sem permissao para anexar arquivo clinico")

        storage_ref = await self._storage_service.salvar(dto.conteudo, dto.nome_arquivo)

        agora = datetime.now(UTC)
        anexo = Anexo(
            id=uuid4(),
            clinica_id=clinica_id,
            criado_em=agora,
            atualizado_em=agora,
            deletado=False,
            deletado_em=None,
            entidade_tipo=entidade_tipo,
            entidade_id=dto.entidade_id,
            tipo_arquivo=TipoArquivo(dto.tipo_arquivo),
            nome_arquivo=dto.nome_arquivo,
            storage_ref=storage_ref,
            criado_por=criado_por,
        )
        salvo = await self._anexo_repository.salvar(anexo)
        return anexo_to_dto(salvo)
