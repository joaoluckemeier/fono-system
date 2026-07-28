from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from backend.application.dtos.auth_dto import UsuarioAutenticadoDTO
from backend.application.dtos.profissional_caso_dto import CriarProfissionalCasoInputDTO
from backend.application.exceptions import RecursoNaoEncontradoError
from backend.application.use_cases.profissionais_caso.criar_profissional import (
    CriarProfissionalUseCase,
)
from backend.application.use_cases.profissionais_caso.deletar_profissional import (
    DeletarProfissionalUseCase,
)
from backend.application.use_cases.profissionais_caso.listar_profissionais import (
    ListarProfissionaisUseCase,
)
from backend.container import (
    get_criar_profissional_use_case,
    get_deletar_profissional_use_case,
    get_listar_profissionais_use_case,
)
from backend.interface.dependencies import get_usuario_atual
from backend.interface.schemas.profissional_caso_schema import (
    ProfissionalCasoCreate,
    ProfissionalCasoResponse,
)

router = APIRouter(tags=["profissionais-caso"])


@router.get("/pacientes/{paciente_id}/profissionais", response_model=list[ProfissionalCasoResponse])
async def listar_profissionais(
    paciente_id: UUID,
    usuario_atual: UsuarioAutenticadoDTO = Depends(get_usuario_atual),
    use_case: ListarProfissionaisUseCase = Depends(get_listar_profissionais_use_case),
) -> list[ProfissionalCasoResponse]:
    profissionais = await use_case.executar(paciente_id, usuario_atual.clinica_id)
    return [ProfissionalCasoResponse(**p.__dict__) for p in profissionais]


@router.post(
    "/pacientes/{paciente_id}/profissionais",
    response_model=ProfissionalCasoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def criar_profissional(
    paciente_id: UUID,
    body: ProfissionalCasoCreate,
    usuario_atual: UsuarioAutenticadoDTO = Depends(get_usuario_atual),
    use_case: CriarProfissionalUseCase = Depends(get_criar_profissional_use_case),
) -> ProfissionalCasoResponse:
    try:
        profissional = await use_case.executar(
            paciente_id,
            CriarProfissionalCasoInputDTO(**body.model_dump()),
            usuario_atual.clinica_id,
        )
    except RecursoNaoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    return ProfissionalCasoResponse(**profissional.__dict__)


@router.delete("/profissionais/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_profissional(
    id: UUID,
    usuario_atual: UsuarioAutenticadoDTO = Depends(get_usuario_atual),
    use_case: DeletarProfissionalUseCase = Depends(get_deletar_profissional_use_case),
) -> None:
    try:
        await use_case.executar(id, usuario_atual.clinica_id)
    except RecursoNaoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
