from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from backend.application.dtos.auth_dto import UsuarioAutenticadoDTO
from backend.application.dtos.modelo_termo_dto import (
    AtualizarModeloTermoInputDTO,
    CriarModeloTermoInputDTO,
)
from backend.application.exceptions import PermissaoNegadaError, RecursoNaoEncontradoError
from backend.application.use_cases.termos.atualizar_modelo_termo import AtualizarModeloTermoUseCase
from backend.application.use_cases.termos.criar_modelo_termo import CriarModeloTermoUseCase
from backend.application.use_cases.termos.deletar_modelo_termo import DeletarModeloTermoUseCase
from backend.application.use_cases.termos.listar_modelos_termo import ListarModelosTermoUseCase
from backend.container import (
    get_atualizar_modelo_termo_use_case,
    get_criar_modelo_termo_use_case,
    get_deletar_modelo_termo_use_case,
    get_listar_modelos_termo_use_case,
)
from backend.domain.entities.usuario import PapelUsuario
from backend.interface.dependencies import get_usuario_atual
from backend.interface.schemas.modelo_termo_schema import (
    ModeloTermoCreate,
    ModeloTermoResponse,
    ModeloTermoUpdate,
)

router = APIRouter(prefix="/modelos-termo", tags=["modelos-termo"])


@router.get("", response_model=list[ModeloTermoResponse])
async def listar_modelos_termo(
    apenas_ativos: bool = False,
    usuario_atual: UsuarioAutenticadoDTO = Depends(get_usuario_atual),
    use_case: ListarModelosTermoUseCase = Depends(get_listar_modelos_termo_use_case),
) -> list[ModeloTermoResponse]:
    try:
        modelos = await use_case.executar(
            usuario_atual.clinica_id, PapelUsuario(usuario_atual.papel), apenas_ativos
        )
    except PermissaoNegadaError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    return [ModeloTermoResponse(**m.__dict__) for m in modelos]


@router.post("", response_model=ModeloTermoResponse, status_code=status.HTTP_201_CREATED)
async def criar_modelo_termo(
    body: ModeloTermoCreate,
    usuario_atual: UsuarioAutenticadoDTO = Depends(get_usuario_atual),
    use_case: CriarModeloTermoUseCase = Depends(get_criar_modelo_termo_use_case),
) -> ModeloTermoResponse:
    try:
        modelo = await use_case.executar(
            CriarModeloTermoInputDTO(**body.model_dump()),
            usuario_atual.clinica_id,
            PapelUsuario(usuario_atual.papel),
        )
    except PermissaoNegadaError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    return ModeloTermoResponse(**modelo.__dict__)


@router.put("/{id}", response_model=ModeloTermoResponse)
async def atualizar_modelo_termo(
    id: UUID,
    body: ModeloTermoUpdate,
    usuario_atual: UsuarioAutenticadoDTO = Depends(get_usuario_atual),
    use_case: AtualizarModeloTermoUseCase = Depends(get_atualizar_modelo_termo_use_case),
) -> ModeloTermoResponse:
    try:
        modelo = await use_case.executar(
            id,
            AtualizarModeloTermoInputDTO(**body.model_dump()),
            usuario_atual.clinica_id,
            PapelUsuario(usuario_atual.papel),
        )
    except PermissaoNegadaError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except RecursoNaoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    return ModeloTermoResponse(**modelo.__dict__)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_modelo_termo(
    id: UUID,
    usuario_atual: UsuarioAutenticadoDTO = Depends(get_usuario_atual),
    use_case: DeletarModeloTermoUseCase = Depends(get_deletar_modelo_termo_use_case),
) -> None:
    try:
        await use_case.executar(id, usuario_atual.clinica_id, PapelUsuario(usuario_atual.papel))
    except PermissaoNegadaError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except RecursoNaoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
