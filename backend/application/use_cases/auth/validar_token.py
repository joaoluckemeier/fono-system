from backend.application.dtos.auth_dto import UsuarioAutenticadoDTO
from backend.application.exceptions import TokenInvalidoOuExpiradoError
from backend.domain.repositories.usuario_repository import UsuarioRepository
from backend.infrastructure.auth.jwt_provider import JWTProvider, TokenInvalidoError


class ValidarTokenUseCase:
    def __init__(self, usuario_repository: UsuarioRepository, jwt_provider: JWTProvider) -> None:
        self._usuario_repository = usuario_repository
        self._jwt_provider = jwt_provider

    async def executar(self, access_token: str) -> UsuarioAutenticadoDTO:
        try:
            payload = self._jwt_provider.decodificar_access_token(access_token)
        except TokenInvalidoError as exc:
            raise TokenInvalidoOuExpiradoError(str(exc)) from exc

        usuario = await self._usuario_repository.buscar_por_id(
            payload.usuario_id, payload.clinica_id
        )
        if usuario is None or not usuario.ativo:
            raise TokenInvalidoOuExpiradoError("Usuario invalido")

        return UsuarioAutenticadoDTO(
            id=usuario.id,
            clinica_id=usuario.clinica_id,
            papel=usuario.papel.value,
            nome=usuario.nome,
            email=usuario.email,
        )
