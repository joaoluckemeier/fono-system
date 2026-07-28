from fastapi import APIRouter, Depends, HTTPException, Request, status

from backend.application.dtos.auth_dto import LoginInputDTO
from backend.application.exceptions import CredenciaisInvalidasError, TokenInvalidoOuExpiradoError
from backend.application.use_cases.auth.login import LoginUseCase
from backend.application.use_cases.auth.refresh_token import RefreshTokenUseCase
from backend.container import get_login_use_case, get_refresh_token_use_case
from backend.interface.dependencies import get_usuario_atual
from backend.interface.middlewares.rate_limit import limiter
from backend.interface.schemas.auth_schema import (
    LoginRequest,
    RefreshRequest,
    TokenResponse,
    UsuarioAutenticadoResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    body: LoginRequest,
    login_use_case: LoginUseCase = Depends(get_login_use_case),
) -> TokenResponse:
    try:
        resultado = await login_use_case.executar(LoginInputDTO(email=body.email, senha=body.senha))
    except CredenciaisInvalidasError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    return TokenResponse(
        access_token=resultado.access_token,
        refresh_token=resultado.refresh_token,
        token_type=resultado.token_type,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    body: RefreshRequest,
    refresh_token_use_case: RefreshTokenUseCase = Depends(get_refresh_token_use_case),
) -> TokenResponse:
    try:
        resultado = await refresh_token_use_case.executar(body.refresh_token)
    except TokenInvalidoOuExpiradoError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    return TokenResponse(
        access_token=resultado.access_token,
        refresh_token=resultado.refresh_token,
        token_type=resultado.token_type,
    )


@router.get("/me", response_model=UsuarioAutenticadoResponse)
async def me(
    usuario_atual: UsuarioAutenticadoResponse = Depends(get_usuario_atual),
) -> UsuarioAutenticadoResponse:
    return usuario_atual
