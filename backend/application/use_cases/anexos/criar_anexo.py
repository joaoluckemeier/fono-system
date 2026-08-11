import re
from datetime import UTC, datetime
from uuid import UUID, uuid4

from backend.application.dtos.anexo_dto import AnexoDTO, CriarAnexoInputDTO, anexo_to_dto
from backend.application.exceptions import PermissaoNegadaError, RecursoNaoEncontradoError
from backend.domain.authorization.policy import RECURSO_POR_ENTIDADE_ANEXO, usuario_pode
from backend.domain.entities.anexo import Anexo, EntidadeAnexavel, TipoArquivo
from backend.domain.entities.usuario import PapelUsuario
from backend.domain.repositories.anexo_repository import AnexoRepository
from backend.domain.repositories.evolucao_repository import EvolucaoRepository
from backend.domain.repositories.paciente_repository import PacienteRepository
from backend.domain.repositories.protocolo_paciente_repository import ProtocoloPacienteRepository
from backend.domain.services.storage_service import StorageServiceInterface

TAMANHO_MAXIMO_ANEXO_BYTES = 25 * 1024 * 1024

_EXTENSOES_POR_TIPO: dict[TipoArquivo, set[str]] = {
    TipoArquivo.PDF: {".pdf"},
    TipoArquivo.FOTO: {".jpg", ".jpeg", ".png", ".webp"},
    TipoArquivo.AUDIO: {".mp3", ".wav", ".m4a", ".ogg"},
    TipoArquivo.VIDEO: {".mp4", ".mov", ".webm"},
}

_ASSINATURAS_BINARIAS: dict[str, bytes] = {
    ".pdf": b"%PDF",
    ".jpg": b"\xff\xd8\xff",
    ".jpeg": b"\xff\xd8\xff",
    ".png": b"\x89PNG",
}

_CARACTERES_INVALIDOS_NOME = re.compile(r"[/\\\x00-\x1f]")


class CriarAnexoUseCase:
    def __init__(
        self,
        anexo_repository: AnexoRepository,
        storage_service: StorageServiceInterface,
        paciente_repository: PacienteRepository,
        evolucao_repository: EvolucaoRepository,
        protocolo_paciente_repository: ProtocoloPacienteRepository,
    ) -> None:
        self._anexo_repository = anexo_repository
        self._storage_service = storage_service
        self._paciente_repository = paciente_repository
        self._evolucao_repository = evolucao_repository
        self._protocolo_paciente_repository = protocolo_paciente_repository

    async def executar(
        self,
        dto: CriarAnexoInputDTO,
        clinica_id: UUID,
        criado_por: UUID,
        papel: PapelUsuario,
    ) -> AnexoDTO:
        entidade_tipo = EntidadeAnexavel(dto.entidade_tipo)
        recurso = RECURSO_POR_ENTIDADE_ANEXO[entidade_tipo]
        if not usuario_pode(papel, recurso):
            raise PermissaoNegadaError("Papel sem permissao para anexar arquivo clinico")

        await self._validar_posse_entidade(entidade_tipo, dto.entidade_id, clinica_id)

        tipo_arquivo = TipoArquivo(dto.tipo_arquivo)
        nome_arquivo = self._validar_arquivo(tipo_arquivo, dto.nome_arquivo, dto.conteudo)

        storage_ref = await self._storage_service.salvar(dto.conteudo, nome_arquivo)

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
            tipo_arquivo=tipo_arquivo,
            nome_arquivo=nome_arquivo,
            storage_ref=storage_ref,
            criado_por=criado_por,
        )
        salvo = await self._anexo_repository.salvar(anexo)
        return anexo_to_dto(salvo)

    async def _validar_posse_entidade(
        self, entidade_tipo: EntidadeAnexavel, entidade_id: UUID, clinica_id: UUID
    ) -> None:
        if entidade_tipo == EntidadeAnexavel.PACIENTE:
            entidade = await self._paciente_repository.buscar_por_id(entidade_id, clinica_id)
        elif entidade_tipo == EntidadeAnexavel.EVOLUCAO:
            entidade = await self._evolucao_repository.buscar_por_id(entidade_id, clinica_id)
        else:
            entidade = await self._protocolo_paciente_repository.buscar_por_id(
                entidade_id, clinica_id
            )

        if entidade is None:
            raise RecursoNaoEncontradoError("Recurso vinculado nao encontrado")

    def _validar_arquivo(
        self, tipo_arquivo: TipoArquivo, nome_arquivo: str, conteudo: bytes
    ) -> str:
        if len(conteudo) > TAMANHO_MAXIMO_ANEXO_BYTES:
            raise ValueError("Arquivo excede o tamanho maximo permitido (25MB)")
        if not conteudo:
            raise ValueError("Arquivo vazio")

        nome_sanitizado = _CARACTERES_INVALIDOS_NOME.sub("", nome_arquivo).strip()[:255]
        if not nome_sanitizado:
            raise ValueError("Nome de arquivo invalido")

        extensoes_permitidas = _EXTENSOES_POR_TIPO.get(tipo_arquivo)
        if extensoes_permitidas is not None:
            extensao = self._extensao(nome_sanitizado)
            if extensao not in extensoes_permitidas:
                raise ValueError(
                    f"Extensao '{extensao}' nao permitida para tipo_arquivo={tipo_arquivo.value}"
                )

            assinatura = _ASSINATURAS_BINARIAS.get(extensao)
            if assinatura is not None and not conteudo.startswith(assinatura):
                raise ValueError("Conteudo do arquivo nao corresponde ao tipo declarado")

        return nome_sanitizado

    @staticmethod
    def _extensao(nome_arquivo: str) -> str:
        indice = nome_arquivo.rfind(".")
        return nome_arquivo[indice:].lower() if indice != -1 else ""
