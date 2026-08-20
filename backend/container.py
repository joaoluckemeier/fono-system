"""Unico arquivo que importa todas as camadas - monta implementacoes concretas
e as expõe como FastAPI Depends. Trocar banco/storage/IA = mudar so aqui.
"""

from collections.abc import AsyncIterator
from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.use_cases.anexos.buscar_url_anexo import BuscarUrlAnexoUseCase
from backend.application.use_cases.anexos.criar_anexo import CriarAnexoUseCase
from backend.application.use_cases.anexos.deletar_anexo import DeletarAnexoUseCase
from backend.application.use_cases.anexos.listar_anexos import ListarAnexosUseCase
from backend.application.use_cases.auth.login import LoginUseCase
from backend.application.use_cases.auth.refresh_token import RefreshTokenUseCase
from backend.application.use_cases.auth.validar_token import ValidarTokenUseCase
from backend.application.use_cases.caa.atualizar_caa import AtualizarCaaUseCase
from backend.application.use_cases.caa.buscar_caa import BuscarCaaUseCase
from backend.application.use_cases.evolucoes.buscar_ultima_devolutiva import (
    BuscarUltimaDevolutivaUseCase,
)
from backend.application.use_cases.evolucoes.confirmar_evolucao import ConfirmarEvolucaoUseCase
from backend.application.use_cases.evolucoes.criar_evolucao import CriarEvolucaoUseCase
from backend.application.use_cases.evolucoes.deletar_evolucao import DeletarEvolucaoUseCase
from backend.application.use_cases.evolucoes.gerar_rascunho_evolucao import (
    GerarRascunhoEvolucaoUseCase,
)
from backend.application.use_cases.evolucoes.listar_evolucoes import ListarEvolucoesUseCase
from backend.application.use_cases.pacientes.atualizar_paciente import AtualizarPacienteUseCase
from backend.application.use_cases.pacientes.atualizar_status_paciente import (
    AtualizarStatusPacienteUseCase,
)
from backend.application.use_cases.pacientes.buscar_paciente import BuscarPacienteUseCase
from backend.application.use_cases.pacientes.criar_paciente import CriarPacienteUseCase
from backend.application.use_cases.pacientes.deletar_paciente import DeletarPacienteUseCase
from backend.application.use_cases.pacientes.listar_pacientes import ListarPacientesUseCase
from backend.application.use_cases.profissionais_caso.criar_profissional import (
    CriarProfissionalUseCase,
)
from backend.application.use_cases.profissionais_caso.deletar_profissional import (
    DeletarProfissionalUseCase,
)
from backend.application.use_cases.profissionais_caso.listar_profissionais import (
    ListarProfissionaisUseCase,
)
from backend.application.use_cases.protocolos.associar_protocolo_paciente import (
    AssociarProtocoloPacienteUseCase,
)
from backend.application.use_cases.protocolos.atualizar_status_protocolo_paciente import (
    AtualizarStatusProtocoloPacienteUseCase,
)
from backend.application.use_cases.protocolos.criar_protocolo import CriarProtocoloUseCase
from backend.application.use_cases.protocolos.deletar_protocolo_paciente import (
    DeletarProtocoloPacienteUseCase,
)
from backend.application.use_cases.protocolos.listar_protocolos import ListarProtocolosUseCase
from backend.application.use_cases.protocolos.listar_protocolos_paciente import (
    ListarProtocolosPacienteUseCase,
)
from backend.application.use_cases.tarefas.atualizar_tarefa import AtualizarTarefaUseCase
from backend.application.use_cases.tarefas.criar_tarefa import CriarTarefaUseCase
from backend.application.use_cases.tarefas.deletar_tarefa import DeletarTarefaUseCase
from backend.application.use_cases.tarefas.duplicar_tarefas import DuplicarTarefasUseCase
from backend.application.use_cases.tarefas.listar_planejamento_semana import (
    ListarPlanejamentoSemanaUseCase,
)
from backend.application.use_cases.tarefas.listar_tarefas_paciente import (
    ListarTarefasPacienteUseCase,
)
from backend.application.use_cases.tarefas.marcar_conclusao_tarefa import (
    MarcarConclusaoTarefaUseCase,
)
from backend.application.use_cases.termos.atualizar_modelo_termo import AtualizarModeloTermoUseCase
from backend.application.use_cases.termos.criar_modelo_termo import CriarModeloTermoUseCase
from backend.application.use_cases.termos.deletar_modelo_termo import DeletarModeloTermoUseCase
from backend.application.use_cases.termos.gerar_termo import GerarTermoUseCase
from backend.application.use_cases.termos.listar_modelos_termo import ListarModelosTermoUseCase
from backend.application.use_cases.termos.listar_termos_gerados import ListarTermosGeradosUseCase
from backend.config import Settings, get_settings
from backend.domain.repositories.anexo_repository import AnexoRepository
from backend.domain.repositories.caa_dados_repository import CaaDadosRepository
from backend.domain.repositories.clinica_repository import ClinicaRepository
from backend.domain.repositories.evolucao_repository import EvolucaoRepository
from backend.domain.repositories.modelo_termo_repository import ModeloTermoRepository
from backend.domain.repositories.paciente_repository import PacienteRepository
from backend.domain.repositories.profissional_caso_repository import ProfissionalCasoRepository
from backend.domain.repositories.protocolo_paciente_repository import ProtocoloPacienteRepository
from backend.domain.repositories.protocolo_repository import ProtocoloRepository
from backend.domain.repositories.refresh_token_repository import RefreshTokenRepository
from backend.domain.repositories.tarefa_repository import TarefaRepository
from backend.domain.repositories.termo_gerado_repository import TermoGeradoRepository
from backend.domain.repositories.usuario_repository import UsuarioRepository
from backend.domain.services.ai_gateway_service import AIGatewayInterface
from backend.domain.services.gerador_documento_service import GeradorDocumentoInterface
from backend.domain.services.storage_service import StorageServiceInterface
from backend.domain.services.transcricao_service import TranscricaoServiceInterface
from backend.infrastructure.ai.ai_gateway_placeholder import (
    AIGatewayPlaceholder,
    TranscricaoServicePlaceholder,
)
from backend.infrastructure.ai.openai_gateway_service import OpenAIGatewayService
from backend.infrastructure.ai.openai_transcricao_service import OpenAITranscricaoService
from backend.infrastructure.audit.audit_logger import AuditLogger
from backend.infrastructure.auth.jwt_provider import JWTProvider
from backend.infrastructure.database.connection import async_session_factory
from backend.infrastructure.documentos.fpdf_gerador_documento import FPDFGeradorDocumento
from backend.infrastructure.repositories.anexo_repository import AnexoRepositoryImpl
from backend.infrastructure.repositories.caa_dados_repository import CaaDadosRepositoryImpl
from backend.infrastructure.repositories.clinica_repository import ClinicaRepositoryImpl
from backend.infrastructure.repositories.evolucao_repository import EvolucaoRepositoryImpl
from backend.infrastructure.repositories.log_acesso_repository import LogAcessoRepositoryImpl
from backend.infrastructure.repositories.modelo_termo_repository import ModeloTermoRepositoryImpl
from backend.infrastructure.repositories.paciente_repository import PacienteRepositoryImpl
from backend.infrastructure.repositories.profissional_caso_repository import (
    ProfissionalCasoRepositoryImpl,
)
from backend.infrastructure.repositories.protocolo_paciente_repository import (
    ProtocoloPacienteRepositoryImpl,
)
from backend.infrastructure.repositories.protocolo_repository import ProtocoloRepositoryImpl
from backend.infrastructure.repositories.refresh_token_repository import RefreshTokenRepositoryImpl
from backend.infrastructure.repositories.tarefa_repository import TarefaRepositoryImpl
from backend.infrastructure.repositories.termo_gerado_repository import TermoGeradoRepositoryImpl
from backend.infrastructure.repositories.usuario_repository import UsuarioRepositoryImpl
from backend.infrastructure.storage.minio_storage import MinIOStorageService


async def get_session() -> AsyncIterator[AsyncSession]:
    async with async_session_factory() as session:
        yield session


@lru_cache
def get_jwt_provider() -> JWTProvider:
    return JWTProvider(get_settings())


@lru_cache
def get_storage_service() -> StorageServiceInterface:
    return MinIOStorageService(get_settings())


@lru_cache
def get_ai_gateway_service() -> AIGatewayInterface:
    settings = get_settings()
    if settings.ai_gateway_modo == "openai" and settings.openai_api_key:
        return OpenAIGatewayService(settings)
    return AIGatewayPlaceholder()


@lru_cache
def get_transcricao_service() -> TranscricaoServiceInterface:
    settings = get_settings()
    if settings.ai_gateway_modo == "openai" and settings.openai_api_key:
        return OpenAITranscricaoService(settings)
    return TranscricaoServicePlaceholder()


@lru_cache
def get_gerador_documento_service() -> GeradorDocumentoInterface:
    return FPDFGeradorDocumento()


def get_app_settings() -> Settings:
    return get_settings()


# --- Repositories ---


def get_usuario_repository(session: AsyncSession = Depends(get_session)) -> UsuarioRepository:
    return UsuarioRepositoryImpl(session)


def get_refresh_token_repository(
    session: AsyncSession = Depends(get_session),
) -> RefreshTokenRepository:
    return RefreshTokenRepositoryImpl(session)


def get_audit_logger(session: AsyncSession = Depends(get_session)) -> AuditLogger:
    return AuditLogger(LogAcessoRepositoryImpl(session))


def get_paciente_repository(session: AsyncSession = Depends(get_session)) -> PacienteRepository:
    return PacienteRepositoryImpl(session)


def get_profissional_caso_repository(
    session: AsyncSession = Depends(get_session),
) -> ProfissionalCasoRepository:
    return ProfissionalCasoRepositoryImpl(session)


def get_protocolo_repository(session: AsyncSession = Depends(get_session)) -> ProtocoloRepository:
    return ProtocoloRepositoryImpl(session)


def get_protocolo_paciente_repository(
    session: AsyncSession = Depends(get_session),
) -> ProtocoloPacienteRepository:
    return ProtocoloPacienteRepositoryImpl(session)


def get_caa_dados_repository(session: AsyncSession = Depends(get_session)) -> CaaDadosRepository:
    return CaaDadosRepositoryImpl(session)


def get_evolucao_repository(session: AsyncSession = Depends(get_session)) -> EvolucaoRepository:
    return EvolucaoRepositoryImpl(session)


def get_anexo_repository(session: AsyncSession = Depends(get_session)) -> AnexoRepository:
    return AnexoRepositoryImpl(session)


def get_tarefa_repository(session: AsyncSession = Depends(get_session)) -> TarefaRepository:
    return TarefaRepositoryImpl(session)


def get_clinica_repository(session: AsyncSession = Depends(get_session)) -> ClinicaRepository:
    return ClinicaRepositoryImpl(session)


def get_modelo_termo_repository(
    session: AsyncSession = Depends(get_session),
) -> ModeloTermoRepository:
    return ModeloTermoRepositoryImpl(session)


def get_termo_gerado_repository(
    session: AsyncSession = Depends(get_session),
) -> TermoGeradoRepository:
    return TermoGeradoRepositoryImpl(session)


# --- Auth use cases ---


def get_login_use_case(
    usuario_repository: UsuarioRepository = Depends(get_usuario_repository),
    refresh_token_repository: RefreshTokenRepository = Depends(get_refresh_token_repository),
    jwt_provider: JWTProvider = Depends(get_jwt_provider),
) -> LoginUseCase:
    return LoginUseCase(usuario_repository, refresh_token_repository, jwt_provider)


def get_refresh_token_use_case(
    usuario_repository: UsuarioRepository = Depends(get_usuario_repository),
    refresh_token_repository: RefreshTokenRepository = Depends(get_refresh_token_repository),
    jwt_provider: JWTProvider = Depends(get_jwt_provider),
) -> RefreshTokenUseCase:
    return RefreshTokenUseCase(usuario_repository, refresh_token_repository, jwt_provider)


def get_validar_token_use_case(
    usuario_repository: UsuarioRepository = Depends(get_usuario_repository),
    jwt_provider: JWTProvider = Depends(get_jwt_provider),
) -> ValidarTokenUseCase:
    return ValidarTokenUseCase(usuario_repository, jwt_provider)


# --- Pacientes use cases ---


def get_criar_paciente_use_case(
    paciente_repository: PacienteRepository = Depends(get_paciente_repository),
) -> CriarPacienteUseCase:
    return CriarPacienteUseCase(paciente_repository)


def get_listar_pacientes_use_case(
    paciente_repository: PacienteRepository = Depends(get_paciente_repository),
) -> ListarPacientesUseCase:
    return ListarPacientesUseCase(paciente_repository)


def get_buscar_paciente_use_case(
    paciente_repository: PacienteRepository = Depends(get_paciente_repository),
) -> BuscarPacienteUseCase:
    return BuscarPacienteUseCase(paciente_repository)


def get_atualizar_paciente_use_case(
    paciente_repository: PacienteRepository = Depends(get_paciente_repository),
) -> AtualizarPacienteUseCase:
    return AtualizarPacienteUseCase(paciente_repository)


def get_deletar_paciente_use_case(
    paciente_repository: PacienteRepository = Depends(get_paciente_repository),
) -> DeletarPacienteUseCase:
    return DeletarPacienteUseCase(paciente_repository)


def get_atualizar_status_paciente_use_case(
    paciente_repository: PacienteRepository = Depends(get_paciente_repository),
) -> AtualizarStatusPacienteUseCase:
    return AtualizarStatusPacienteUseCase(paciente_repository)


# --- Profissionais do caso use cases ---


def get_criar_profissional_use_case(
    profissional_repository: ProfissionalCasoRepository = Depends(get_profissional_caso_repository),
    paciente_repository: PacienteRepository = Depends(get_paciente_repository),
) -> CriarProfissionalUseCase:
    return CriarProfissionalUseCase(profissional_repository, paciente_repository)


def get_listar_profissionais_use_case(
    profissional_repository: ProfissionalCasoRepository = Depends(get_profissional_caso_repository),
) -> ListarProfissionaisUseCase:
    return ListarProfissionaisUseCase(profissional_repository)


def get_deletar_profissional_use_case(
    profissional_repository: ProfissionalCasoRepository = Depends(get_profissional_caso_repository),
) -> DeletarProfissionalUseCase:
    return DeletarProfissionalUseCase(profissional_repository)


# --- Protocolos use cases ---


def get_criar_protocolo_use_case(
    protocolo_repository: ProtocoloRepository = Depends(get_protocolo_repository),
) -> CriarProtocoloUseCase:
    return CriarProtocoloUseCase(protocolo_repository)


def get_listar_protocolos_use_case(
    protocolo_repository: ProtocoloRepository = Depends(get_protocolo_repository),
) -> ListarProtocolosUseCase:
    return ListarProtocolosUseCase(protocolo_repository)


def get_associar_protocolo_paciente_use_case(
    protocolo_paciente_repository: ProtocoloPacienteRepository = Depends(
        get_protocolo_paciente_repository
    ),
    paciente_repository: PacienteRepository = Depends(get_paciente_repository),
    protocolo_repository: ProtocoloRepository = Depends(get_protocolo_repository),
) -> AssociarProtocoloPacienteUseCase:
    return AssociarProtocoloPacienteUseCase(
        protocolo_paciente_repository, paciente_repository, protocolo_repository
    )


def get_listar_protocolos_paciente_use_case(
    protocolo_paciente_repository: ProtocoloPacienteRepository = Depends(
        get_protocolo_paciente_repository
    ),
) -> ListarProtocolosPacienteUseCase:
    return ListarProtocolosPacienteUseCase(protocolo_paciente_repository)


def get_atualizar_status_protocolo_paciente_use_case(
    protocolo_paciente_repository: ProtocoloPacienteRepository = Depends(
        get_protocolo_paciente_repository
    ),
) -> AtualizarStatusProtocoloPacienteUseCase:
    return AtualizarStatusProtocoloPacienteUseCase(protocolo_paciente_repository)


def get_deletar_protocolo_paciente_use_case(
    protocolo_paciente_repository: ProtocoloPacienteRepository = Depends(
        get_protocolo_paciente_repository
    ),
) -> DeletarProtocoloPacienteUseCase:
    return DeletarProtocoloPacienteUseCase(protocolo_paciente_repository)


# --- CAA use cases ---


def get_buscar_caa_use_case(
    caa_dados_repository: CaaDadosRepository = Depends(get_caa_dados_repository),
) -> BuscarCaaUseCase:
    return BuscarCaaUseCase(caa_dados_repository)


def get_atualizar_caa_use_case(
    caa_dados_repository: CaaDadosRepository = Depends(get_caa_dados_repository),
    paciente_repository: PacienteRepository = Depends(get_paciente_repository),
) -> AtualizarCaaUseCase:
    return AtualizarCaaUseCase(caa_dados_repository, paciente_repository)


# --- Evolucoes use cases ---


def get_criar_evolucao_use_case(
    evolucao_repository: EvolucaoRepository = Depends(get_evolucao_repository),
    paciente_repository: PacienteRepository = Depends(get_paciente_repository),
) -> CriarEvolucaoUseCase:
    return CriarEvolucaoUseCase(evolucao_repository, paciente_repository)


def get_listar_evolucoes_use_case(
    evolucao_repository: EvolucaoRepository = Depends(get_evolucao_repository),
) -> ListarEvolucoesUseCase:
    return ListarEvolucoesUseCase(evolucao_repository)


def get_buscar_ultima_devolutiva_use_case(
    evolucao_repository: EvolucaoRepository = Depends(get_evolucao_repository),
) -> BuscarUltimaDevolutivaUseCase:
    return BuscarUltimaDevolutivaUseCase(evolucao_repository)


def get_gerar_rascunho_evolucao_use_case(
    evolucao_repository: EvolucaoRepository = Depends(get_evolucao_repository),
    paciente_repository: PacienteRepository = Depends(get_paciente_repository),
    storage_service: StorageServiceInterface = Depends(get_storage_service),
    transcricao_service: TranscricaoServiceInterface = Depends(get_transcricao_service),
    ai_gateway: AIGatewayInterface = Depends(get_ai_gateway_service),
) -> GerarRascunhoEvolucaoUseCase:
    return GerarRascunhoEvolucaoUseCase(
        evolucao_repository, paciente_repository, storage_service, transcricao_service, ai_gateway
    )


def get_confirmar_evolucao_use_case(
    evolucao_repository: EvolucaoRepository = Depends(get_evolucao_repository),
    storage_service: StorageServiceInterface = Depends(get_storage_service),
) -> ConfirmarEvolucaoUseCase:
    return ConfirmarEvolucaoUseCase(evolucao_repository, storage_service)


def get_deletar_evolucao_use_case(
    evolucao_repository: EvolucaoRepository = Depends(get_evolucao_repository),
    storage_service: StorageServiceInterface = Depends(get_storage_service),
) -> DeletarEvolucaoUseCase:
    return DeletarEvolucaoUseCase(evolucao_repository, storage_service)


# --- Tarefas (planejamento terapeutico semanal) use cases ---


def get_criar_tarefa_use_case(
    tarefa_repository: TarefaRepository = Depends(get_tarefa_repository),
    paciente_repository: PacienteRepository = Depends(get_paciente_repository),
) -> CriarTarefaUseCase:
    return CriarTarefaUseCase(tarefa_repository, paciente_repository)


def get_listar_tarefas_paciente_use_case(
    tarefa_repository: TarefaRepository = Depends(get_tarefa_repository),
) -> ListarTarefasPacienteUseCase:
    return ListarTarefasPacienteUseCase(tarefa_repository)


def get_listar_planejamento_semana_use_case(
    tarefa_repository: TarefaRepository = Depends(get_tarefa_repository),
    paciente_repository: PacienteRepository = Depends(get_paciente_repository),
) -> ListarPlanejamentoSemanaUseCase:
    return ListarPlanejamentoSemanaUseCase(tarefa_repository, paciente_repository)


def get_atualizar_tarefa_use_case(
    tarefa_repository: TarefaRepository = Depends(get_tarefa_repository),
) -> AtualizarTarefaUseCase:
    return AtualizarTarefaUseCase(tarefa_repository)


def get_marcar_conclusao_tarefa_use_case(
    tarefa_repository: TarefaRepository = Depends(get_tarefa_repository),
) -> MarcarConclusaoTarefaUseCase:
    return MarcarConclusaoTarefaUseCase(tarefa_repository)


def get_duplicar_tarefas_use_case(
    tarefa_repository: TarefaRepository = Depends(get_tarefa_repository),
) -> DuplicarTarefasUseCase:
    return DuplicarTarefasUseCase(tarefa_repository)


def get_deletar_tarefa_use_case(
    tarefa_repository: TarefaRepository = Depends(get_tarefa_repository),
) -> DeletarTarefaUseCase:
    return DeletarTarefaUseCase(tarefa_repository)


# --- Anexos use cases ---


def get_criar_anexo_use_case(
    anexo_repository: AnexoRepository = Depends(get_anexo_repository),
    storage_service: StorageServiceInterface = Depends(get_storage_service),
    paciente_repository: PacienteRepository = Depends(get_paciente_repository),
    evolucao_repository: EvolucaoRepository = Depends(get_evolucao_repository),
    protocolo_paciente_repository: ProtocoloPacienteRepository = Depends(
        get_protocolo_paciente_repository
    ),
) -> CriarAnexoUseCase:
    return CriarAnexoUseCase(
        anexo_repository,
        storage_service,
        paciente_repository,
        evolucao_repository,
        protocolo_paciente_repository,
    )


def get_listar_anexos_use_case(
    anexo_repository: AnexoRepository = Depends(get_anexo_repository),
) -> ListarAnexosUseCase:
    return ListarAnexosUseCase(anexo_repository)


def get_deletar_anexo_use_case(
    anexo_repository: AnexoRepository = Depends(get_anexo_repository),
    storage_service: StorageServiceInterface = Depends(get_storage_service),
) -> DeletarAnexoUseCase:
    return DeletarAnexoUseCase(anexo_repository, storage_service)


def get_buscar_url_anexo_use_case(
    anexo_repository: AnexoRepository = Depends(get_anexo_repository),
    storage_service: StorageServiceInterface = Depends(get_storage_service),
) -> BuscarUrlAnexoUseCase:
    return BuscarUrlAnexoUseCase(anexo_repository, storage_service)


# --- Termos e encaminhamentos use cases ---


def get_criar_modelo_termo_use_case(
    modelo_termo_repository: ModeloTermoRepository = Depends(get_modelo_termo_repository),
) -> CriarModeloTermoUseCase:
    return CriarModeloTermoUseCase(modelo_termo_repository)


def get_listar_modelos_termo_use_case(
    modelo_termo_repository: ModeloTermoRepository = Depends(get_modelo_termo_repository),
) -> ListarModelosTermoUseCase:
    return ListarModelosTermoUseCase(modelo_termo_repository)


def get_atualizar_modelo_termo_use_case(
    modelo_termo_repository: ModeloTermoRepository = Depends(get_modelo_termo_repository),
) -> AtualizarModeloTermoUseCase:
    return AtualizarModeloTermoUseCase(modelo_termo_repository)


def get_deletar_modelo_termo_use_case(
    modelo_termo_repository: ModeloTermoRepository = Depends(get_modelo_termo_repository),
) -> DeletarModeloTermoUseCase:
    return DeletarModeloTermoUseCase(modelo_termo_repository)


def get_gerar_termo_use_case(
    modelo_termo_repository: ModeloTermoRepository = Depends(get_modelo_termo_repository),
    paciente_repository: PacienteRepository = Depends(get_paciente_repository),
    clinica_repository: ClinicaRepository = Depends(get_clinica_repository),
    termo_gerado_repository: TermoGeradoRepository = Depends(get_termo_gerado_repository),
    anexo_repository: AnexoRepository = Depends(get_anexo_repository),
    storage_service: StorageServiceInterface = Depends(get_storage_service),
    gerador_documento: GeradorDocumentoInterface = Depends(get_gerador_documento_service),
) -> GerarTermoUseCase:
    return GerarTermoUseCase(
        modelo_termo_repository,
        paciente_repository,
        clinica_repository,
        termo_gerado_repository,
        anexo_repository,
        storage_service,
        gerador_documento,
    )


def get_listar_termos_gerados_use_case(
    termo_gerado_repository: TermoGeradoRepository = Depends(get_termo_gerado_repository),
) -> ListarTermosGeradosUseCase:
    return ListarTermosGeradosUseCase(termo_gerado_repository)
