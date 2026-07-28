from datetime import UTC, datetime
from uuid import uuid4

from backend.application.dtos.auth_dto import TokenParDTO
from backend.application.exceptions import TokenInvalidoOuExpiradoError
from backend.domain.entities.refresh_token import RefreshToken
from backend.domain.repositories.refresh_token_repository import RefreshTokenRepository
from backend.domain.repositories.usuario_repository import UsuarioRepository
from backend.infrastructure.auth.jwt_provider import JWTProvider


class RefreshTokenUseCase:
    def __init__(
        self,
        usuario_repository: UsuarioRepository,
        refresh_token_repository: RefreshTokenRepository,
        jwt_provider: JWTProvider,
    ) -> None:
        self._usuario_repository = usuario_repository
        self._refresh_token_repository = refresh_token_repository
        self._jwt_provider = jwt_provider

    async def executar(self, refresh_token_raw: str) -> TokenParDTO:
        token_hash = JWTProvider.hash_refresh_token(refresh_token_raw)
        token_atual = await self._refresh_token_repository.buscar_por_token_hash(token_hash)

        agora = datetime.now(UTC)
        if (
            token_atual is None
            or token_atual.revogado
            or token_atual.deletado
            or token_atual.expira_em < agora
        ):
            raise TokenInvalidoOuExpiradoError("Refresh token invalido ou expirado")

        usuario = await self._usuario_repository.buscar_por_id(
            token_atual.usuario_id, token_atual.clinica_id
        )
        if usuario is None or not usuario.ativo:
            raise TokenInvalidoOuExpiradoError("Usuario invalido")

        await self._refresh_token_repository.revogar(token_hash)

        novo_refresh_raw = JWTProvider.gerar_refresh_token_raw()
        novo_refresh_hash = JWTProvider.hash_refresh_token(novo_refresh_raw)
        await self._refresh_token_repository.salvar(
            RefreshToken(
                id=uuid4(),
                clinica_id=usuario.clinica_id,
                criado_em=agora,
                atualizado_em=agora,
                deletado=False,
                deletado_em=None,
                usuario_id=usuario.id,
                token_hash=novo_refresh_hash,
                expira_em=self._jwt_provider.gerar_refresh_token_expiracao(),
                revogado=False,
            )
        )

        novo_access = self._jwt_provider.criar_access_token(
            usuario_id=usuario.id, clinica_id=usuario.clinica_id, papel=usuario.papel.value
        )

        return TokenParDTO(access_token=novo_access, refresh_token=novo_refresh_raw)
