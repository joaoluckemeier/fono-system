from datetime import UTC, datetime
from uuid import uuid4

from backend.application.dtos.auth_dto import LoginInputDTO, TokenParDTO
from backend.application.exceptions import CredenciaisInvalidasError
from backend.domain.entities.refresh_token import RefreshToken
from backend.domain.repositories.refresh_token_repository import RefreshTokenRepository
from backend.domain.repositories.usuario_repository import UsuarioRepository
from backend.infrastructure.auth.jwt_provider import JWTProvider
from backend.infrastructure.auth.password_hasher import verificar_senha


class LoginUseCase:
    def __init__(
        self,
        usuario_repository: UsuarioRepository,
        refresh_token_repository: RefreshTokenRepository,
        jwt_provider: JWTProvider,
    ) -> None:
        self._usuario_repository = usuario_repository
        self._refresh_token_repository = refresh_token_repository
        self._jwt_provider = jwt_provider

    async def executar(self, dto: LoginInputDTO) -> TokenParDTO:
        usuario = await self._usuario_repository.buscar_por_email(dto.email)
        if usuario is None or not usuario.ativo:
            raise CredenciaisInvalidasError("Email ou senha invalidos")

        if not verificar_senha(usuario.senha_hash, dto.senha):
            raise CredenciaisInvalidasError("Email ou senha invalidos")

        access_token = self._jwt_provider.criar_access_token(
            usuario_id=usuario.id, clinica_id=usuario.clinica_id, papel=usuario.papel.value
        )

        refresh_token_raw = JWTProvider.gerar_refresh_token_raw()
        refresh_token_hash = JWTProvider.hash_refresh_token(refresh_token_raw)
        agora = datetime.now(UTC)
        await self._refresh_token_repository.salvar(
            RefreshToken(
                id=uuid4(),
                clinica_id=usuario.clinica_id,
                criado_em=agora,
                atualizado_em=agora,
                deletado=False,
                deletado_em=None,
                usuario_id=usuario.id,
                token_hash=refresh_token_hash,
                expira_em=self._jwt_provider.gerar_refresh_token_expiracao(),
                revogado=False,
            )
        )

        usuario.ultimo_login_em = agora
        await self._usuario_repository.salvar(usuario)

        return TokenParDTO(access_token=access_token, refresh_token=refresh_token_raw)
