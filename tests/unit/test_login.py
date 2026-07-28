from datetime import UTC, datetime
from uuid import uuid4

import pytest

from backend.application.dtos.auth_dto import LoginInputDTO
from backend.application.exceptions import CredenciaisInvalidasError
from backend.application.use_cases.auth.login import LoginUseCase
from backend.domain.entities.usuario import PapelUsuario, Usuario
from backend.infrastructure.auth.jwt_provider import JWTProvider
from backend.infrastructure.auth.password_hasher import hash_senha
from tests.unit.fakes import FakeRefreshTokenRepository, FakeUsuarioRepository


def _usuario_beta() -> Usuario:
    agora = datetime.now(UTC)
    return Usuario(
        id=uuid4(),
        clinica_id=uuid4(),
        criado_em=agora,
        atualizado_em=agora,
        deletado=False,
        deletado_em=None,
        email="beta@clinica.com",
        senha_hash=hash_senha("senha_correta"),
        nome="Beta",
        papel=PapelUsuario.ADMIN,
        ativo=True,
        ultimo_login_em=None,
    )


def _login_use_case(usuario_repository: FakeUsuarioRepository, settings) -> LoginUseCase:
    return LoginUseCase(
        usuario_repository=usuario_repository,
        refresh_token_repository=FakeRefreshTokenRepository(),
        jwt_provider=JWTProvider(settings),
    )


async def test_login_credenciais_corretas(settings):
    usuario = _usuario_beta()
    use_case = _login_use_case(FakeUsuarioRepository([usuario]), settings)

    resultado = await use_case.executar(LoginInputDTO(email=usuario.email, senha="senha_correta"))

    assert resultado.access_token
    assert resultado.refresh_token
    assert resultado.token_type == "bearer"


async def test_login_senha_incorreta(settings):
    usuario = _usuario_beta()
    use_case = _login_use_case(FakeUsuarioRepository([usuario]), settings)

    with pytest.raises(CredenciaisInvalidasError):
        await use_case.executar(LoginInputDTO(email=usuario.email, senha="senha_errada"))


async def test_login_usuario_inexistente(settings):
    use_case = _login_use_case(FakeUsuarioRepository([]), settings)

    with pytest.raises(CredenciaisInvalidasError):
        await use_case.executar(LoginInputDTO(email="nao-existe@clinica.com", senha="qualquer"))


async def test_login_usuario_inativo(settings):
    usuario = _usuario_beta()
    usuario.ativo = False
    use_case = _login_use_case(FakeUsuarioRepository([usuario]), settings)

    with pytest.raises(CredenciaisInvalidasError):
        await use_case.executar(LoginInputDTO(email=usuario.email, senha="senha_correta"))
