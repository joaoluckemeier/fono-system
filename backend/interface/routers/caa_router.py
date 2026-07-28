from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from backend.application.dtos.auth_dto import UsuarioAutenticadoDTO
from backend.application.dtos.caa_dados_dto import AtualizarCaaInputDTO
from backend.application.exceptions import PermissaoNegadaError, RecursoNaoEncontradoError
from backend.application.use_cases.caa.atualizar_caa import AtualizarCaaUseCase
from backend.application.use_cases.caa.buscar_caa import BuscarCaaUseCase
from backend.container import get_atualizar_caa_use_case, get_buscar_caa_use_case
from backend.domain.entities.usuario import PapelUsuario
from backend.interface.dependencies import get_usuario_atual
from backend.interface.schemas.caa_schema import CaaResponse, CaaUpdate

router = APIRouter(tags=["caa"])


@router.get("/pacientes/{paciente_id}/caa", response_model=CaaResponse)
async def buscar_caa(
    paciente_id: UUID,
    usuario_atual: UsuarioAutenticadoDTO = Depends(get_usuario_atual),
    use_case: BuscarCaaUseCase = Depends(get_buscar_caa_use_case),
) -> CaaResponse:
    try:
        caa = await use_case.executar(
            paciente_id, usuario_atual.clinica_id, PapelUsuario(usuario_atual.papel)
        )
    except PermissaoNegadaError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except RecursoNaoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return CaaResponse(**caa.__dict__)


@router.put("/pacientes/{paciente_id}/caa", response_model=CaaResponse)
async def atualizar_caa(
    paciente_id: UUID,
    body: CaaUpdate,
    usuario_atual: UsuarioAutenticadoDTO = Depends(get_usuario_atual),
    use_case: AtualizarCaaUseCase = Depends(get_atualizar_caa_use_case),
) -> CaaResponse:
    try:
        caa = await use_case.executar(
            paciente_id,
            AtualizarCaaInputDTO(**body.model_dump()),
            usuario_atual.clinica_id,
            PapelUsuario(usuario_atual.papel),
        )
    except PermissaoNegadaError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except RecursoNaoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return CaaResponse(**caa.__dict__)
