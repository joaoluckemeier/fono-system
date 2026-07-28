import re
from datetime import UTC, date, datetime
from uuid import UUID, uuid4

from backend.application.dtos.evolucao_dto import EvolucaoDTO, evolucao_to_dto
from backend.application.exceptions import PermissaoNegadaError, RecursoNaoEncontradoError
from backend.domain.authorization.policy import Recurso, usuario_pode
from backend.domain.entities.evolucao import Evolucao, StatusEvolucao
from backend.domain.entities.paciente import Paciente
from backend.domain.entities.usuario import PapelUsuario
from backend.domain.repositories.evolucao_repository import EvolucaoRepository
from backend.domain.repositories.paciente_repository import PacienteRepository
from backend.domain.services.ai_gateway_service import AIGatewayInterface
from backend.domain.services.storage_service import StorageServiceInterface
from backend.domain.services.transcricao_service import TranscricaoServiceInterface


def _sanitizar_transcricao(texto: str, paciente: Paciente) -> str:
    """Remove o nome do paciente antes de mandar o texto pra um provedor de IA externo -
    minimizacao de dado (ver docs/ia-preparacao.md). Best-effort: substituicao textual do
    nome completo e do primeiro nome, case-insensitive.
    """
    nomes = {paciente.nome_completo, paciente.nome_completo.split()[0]}
    resultado = texto
    for nome in nomes:
        if nome:
            resultado = re.sub(re.escape(nome), "[paciente]", resultado, flags=re.IGNORECASE)
    return resultado


class GerarRascunhoEvolucaoUseCase:
    def __init__(
        self,
        evolucao_repository: EvolucaoRepository,
        paciente_repository: PacienteRepository,
        storage_service: StorageServiceInterface,
        transcricao_service: TranscricaoServiceInterface,
        ai_gateway: AIGatewayInterface,
    ) -> None:
        self._evolucao_repository = evolucao_repository
        self._paciente_repository = paciente_repository
        self._storage_service = storage_service
        self._transcricao_service = transcricao_service
        self._ai_gateway = ai_gateway

    async def executar(
        self,
        paciente_id: UUID,
        audio_bytes: bytes,
        nome_arquivo: str,
        clinica_id: UUID,
        usuario_id: UUID,
        papel: PapelUsuario,
    ) -> EvolucaoDTO:
        if not usuario_pode(papel, Recurso.EVOLUCAO):
            raise PermissaoNegadaError("Papel sem permissao para gerar evolucao clinica")

        paciente = await self._paciente_repository.buscar_por_id(paciente_id, clinica_id)
        if paciente is None:
            raise RecursoNaoEncontradoError("Paciente nao encontrado")

        audio_ref = await self._storage_service.salvar(audio_bytes, nome_arquivo)

        texto_transcrito = await self._transcricao_service.transcrever(audio_bytes, nome_arquivo)
        texto_sanitizado = _sanitizar_transcricao(texto_transcrito, paciente)
        rascunho = await self._ai_gateway.gerar_rascunho(texto_sanitizado)

        agora = datetime.now(UTC)
        evolucao = Evolucao(
            id=uuid4(),
            clinica_id=clinica_id,
            criado_em=agora,
            atualizado_em=agora,
            deletado=False,
            deletado_em=None,
            paciente_id=paciente_id,
            usuario_id=usuario_id,
            data=date.today(),
            texto=rascunho,
            status=StatusEvolucao.PENDENTE_REVISAO,
            audio_ref=audio_ref,
        )
        salvo = await self._evolucao_repository.salvar(evolucao)
        return evolucao_to_dto(salvo)
