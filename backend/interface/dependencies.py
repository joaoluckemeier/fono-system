from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.application.dtos.auth_dto import UsuarioAutenticadoDTO
from backend.application.exceptions import TokenInvalidoOuExpiradoError
from backend.application.use_cases.auth.validar_token import ValidarTokenUseCase
from backend.container import get_validar_token_use_case

_bearer_scheme = HTTPBearer(auto_error=False)


async def get_usuario_atual(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    validar_token_use_case: ValidarTokenUseCase = Depends(get_validar_token_use_case),
) -> UsuarioAutenticadoDTO:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        usuario = await validar_token_use_case.executar(credentials.credentials)
    except TokenInvalidoOuExpiradoError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated") from exc

    request.state.usuario_atual = usuario
    return usuario
