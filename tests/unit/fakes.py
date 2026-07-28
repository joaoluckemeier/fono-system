"""Repositorios fake em memoria - usados so nos testes unitarios (sem banco)."""

from datetime import datetime
from uuid import UUID

from backend.domain.entities.evolucao import Evolucao, StatusEvolucao
from backend.domain.entities.paciente import Paciente
from backend.domain.entities.refresh_token import RefreshToken
from backend.domain.entities.usuario import Usuario
from backend.domain.repositories.evolucao_repository import EvolucaoRepository
from backend.domain.repositories.paciente_repository import PacienteRepository
from backend.domain.repositories.refresh_token_repository import RefreshTokenRepository
from backend.domain.repositories.usuario_repository import UsuarioRepository
from backend.domain.services.ai_gateway_service import AIGatewayInterface
from backend.domain.services.storage_service import StorageServiceInterface
from backend.domain.services.transcricao_service import TranscricaoServiceInterface


class FakeUsuarioRepository(UsuarioRepository):
    def __init__(self, usuarios: list[Usuario] | None = None) -> None:
        self._usuarios: dict[UUID, Usuario] = {u.id: u for u in (usuarios or [])}

    async def salvar(self, entidade: Usuario) -> Usuario:
        self._usuarios[entidade.id] = entidade
        return entidade

    async def buscar_por_id(self, id: UUID, clinica_id: UUID) -> Usuario | None:
        usuario = self._usuarios.get(id)
        if usuario is None or usuario.clinica_id != clinica_id or usuario.deletado:
            return None
        return usuario

    async def listar(self, clinica_id: UUID) -> list[Usuario]:
        return [
            u for u in self._usuarios.values() if u.clinica_id == clinica_id and not u.deletado
        ]

    async def soft_delete(self, id: UUID, clinica_id: UUID) -> None:
        usuario = self._usuarios.get(id)
        if usuario is not None and usuario.clinica_id == clinica_id:
            usuario.deletado = True
            usuario.deletado_em = datetime.now()

    async def buscar_por_email(self, email: str) -> Usuario | None:
        for usuario in self._usuarios.values():
            if usuario.email == email and not usuario.deletado:
                return usuario
        return None


class FakeRefreshTokenRepository(RefreshTokenRepository):
    def __init__(self) -> None:
        self._tokens: dict[UUID, RefreshToken] = {}

    async def salvar(self, entidade: RefreshToken) -> RefreshToken:
        self._tokens[entidade.id] = entidade
        return entidade

    async def buscar_por_id(self, id: UUID, clinica_id: UUID) -> RefreshToken | None:
        token = self._tokens.get(id)
        if token is None or token.clinica_id != clinica_id:
            return None
        return token

    async def listar(self, clinica_id: UUID) -> list[RefreshToken]:
        return [t for t in self._tokens.values() if t.clinica_id == clinica_id]

    async def soft_delete(self, id: UUID, clinica_id: UUID) -> None:
        token = self._tokens.get(id)
        if token is not None and token.clinica_id == clinica_id:
            token.deletado = True

    async def buscar_por_token_hash(self, token_hash: str) -> RefreshToken | None:
        for token in self._tokens.values():
            if token.token_hash == token_hash and not token.deletado:
                return token
        return None

    async def revogar(self, token_hash: str) -> None:
        for token in self._tokens.values():
            if token.token_hash == token_hash:
                token.revogado = True


class FakePacienteRepository(PacienteRepository):
    def __init__(self) -> None:
        self._pacientes: dict[UUID, Paciente] = {}

    async def salvar(self, entidade: Paciente) -> Paciente:
        self._pacientes[entidade.id] = entidade
        return entidade

    async def buscar_por_id(self, id: UUID, clinica_id: UUID) -> Paciente | None:
        paciente = self._pacientes.get(id)
        if paciente is None or paciente.clinica_id != clinica_id or paciente.deletado:
            return None
        return paciente

    async def listar(self, clinica_id: UUID) -> list[Paciente]:
        return [
            p for p in self._pacientes.values() if p.clinica_id == clinica_id and not p.deletado
        ]

    async def soft_delete(self, id: UUID, clinica_id: UUID) -> None:
        paciente = self._pacientes.get(id)
        if paciente is not None and paciente.clinica_id == clinica_id:
            paciente.deletado = True
            paciente.deletado_em = datetime.now()


class FakeEvolucaoRepository(EvolucaoRepository):
    def __init__(self) -> None:
        self._evolucoes: dict[UUID, Evolucao] = {}

    async def salvar(self, entidade: Evolucao) -> Evolucao:
        self._evolucoes[entidade.id] = entidade
        return entidade

    async def buscar_por_id(self, id: UUID, clinica_id: UUID) -> Evolucao | None:
        evolucao = self._evolucoes.get(id)
        if evolucao is None or evolucao.clinica_id != clinica_id or evolucao.deletado:
            return None
        return evolucao

    async def listar(self, clinica_id: UUID) -> list[Evolucao]:
        return [
            e for e in self._evolucoes.values() if e.clinica_id == clinica_id and not e.deletado
        ]

    async def soft_delete(self, id: UUID, clinica_id: UUID) -> None:
        evolucao = self._evolucoes.get(id)
        if evolucao is not None and evolucao.clinica_id == clinica_id:
            evolucao.deletado = True
            evolucao.deletado_em = datetime.now()

    async def listar_por_paciente(self, paciente_id: UUID, clinica_id: UUID) -> list[Evolucao]:
        return sorted(
            (
                e
                for e in self._evolucoes.values()
                if e.paciente_id == paciente_id and e.clinica_id == clinica_id and not e.deletado
            ),
            key=lambda e: e.data,
            reverse=True,
        )

    async def buscar_ultima(self, paciente_id: UUID, clinica_id: UUID) -> Evolucao | None:
        registros = [
            e
            for e in await self.listar_por_paciente(paciente_id, clinica_id)
            if e.status is StatusEvolucao.CONFIRMADA
        ]
        return registros[0] if registros else None


class FakeStorageService(StorageServiceInterface):
    def __init__(self) -> None:
        self.salvos: dict[str, bytes] = {}
        self.deletados: list[str] = []

    async def salvar(self, conteudo: bytes, nome_arquivo: str) -> str:
        ref = f"fake://{nome_arquivo}"
        self.salvos[ref] = conteudo
        return ref

    async def obter_url(self, storage_ref: str) -> str:
        return storage_ref

    async def deletar(self, storage_ref: str) -> None:
        self.deletados.append(storage_ref)
        self.salvos.pop(storage_ref, None)


class FakeTranscricaoService(TranscricaoServiceInterface):
    def __init__(self, texto: str = "transcricao de teste") -> None:
        self._texto = texto

    async def transcrever(self, audio_bytes: bytes, nome_arquivo: str) -> str:
        return self._texto


class FakeAIGateway(AIGatewayInterface):
    def __init__(self, rascunho: str = "rascunho de teste") -> None:
        self._rascunho = rascunho
        self.ultimo_contexto: str | None = None

    async def gerar_rascunho(self, contexto_sanitizado: str) -> str:
        self.ultimo_contexto = contexto_sanitizado
        return self._rascunho
