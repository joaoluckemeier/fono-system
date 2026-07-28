from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status

from backend.application.dtos.auth_dto import UsuarioAutenticadoDTO
from backend.application.dtos.evolucao_dto import ConfirmarEvolucaoInputDTO, CriarEvolucaoInputDTO
from backend.application.exceptions import PermissaoNegadaError, RecursoNaoEncontradoError
from backend.application.use_cases.evolucoes.buscar_ultima_devolutiva import (
    BuscarUltimaDevolutivaUseCase,
)
from backend.application.use_cases.evolucoes.confirmar_evolucao import ConfirmarEvolucaoUseCase
from backend.application.use_cases.evolucoes.criar_evolucao import CriarEvolucaoUseCase
from backend.application.use_cases.evolucoes.deletar_evolucao import DeletarEvolucaoUseCase
from backend.application.use_cases.evolucoes.gerar_rascunho_evolucao import (
    GerarRascunhoEvolucaoUseCase,
)
from backend.application.use_cases.evolucoes.listar_evolucoes import ListarEvolucoesUseCase
from backend.container import (
    get_buscar_ultima_devolutiva_use_case,
    get_confirmar_evolucao_use_case,
    get_criar_evolucao_use_case,
    get_deletar_evolucao_use_case,
    get_gerar_rascunho_evolucao_use_case,
    get_listar_evolucoes_use_case,
)
from backend.domain.entities.log_acesso import AcaoAuditoria
from backend.domain.entities.usuario import PapelUsuario
from backend.interface.dependencies import get_usuario_atual
from backend.interface.schemas.evolucao_schema import (
    ConfirmarEvolucaoRequest,
    EvolucaoCreate,
    EvolucaoResponse,
)

router = APIRouter(tags=["evolucoes"])


@router.get("/pacientes/{paciente_id}/evolucoes", response_model=list[EvolucaoResponse])
async def listar_evolucoes(
    paciente_id: UUID,
    request: Request,
    usuario_atual: UsuarioAutenticadoDTO = Depends(get_usuario_atual),
    use_case: ListarEvolucoesUseCase = Depends(get_listar_evolucoes_use_case),
) -> list[EvolucaoResponse]:
    try:
        evolucoes = await use_case.executar(
            paciente_id, usuario_atual.clinica_id, PapelUsuario(usuario_atual.papel)
        )
    except PermissaoNegadaError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    request.state.auditoria = {
        "acao": AcaoAuditoria.VISUALIZAR,
        "entidade_tipo": "evolucao",
        "entidade_id": paciente_id,
    }
    return [EvolucaoResponse(**e.__dict__) for e in evolucoes]


@router.post(
    "/pacientes/{paciente_id}/evolucoes",
    response_model=EvolucaoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def criar_evolucao(
    paciente_id: UUID,
    body: EvolucaoCreate,
    request: Request,
    usuario_atual: UsuarioAutenticadoDTO = Depends(get_usuario_atual),
    use_case: CriarEvolucaoUseCase = Depends(get_criar_evolucao_use_case),
) -> EvolucaoResponse:
    try:
        evolucao = await use_case.executar(
            paciente_id,
            CriarEvolucaoInputDTO(**body.model_dump()),
            usuario_atual.clinica_id,
            usuario_atual.id,
            PapelUsuario(usuario_atual.papel),
        )
    except PermissaoNegadaError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except RecursoNaoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    request.state.auditoria = {
        "acao": AcaoAuditoria.CRIAR,
        "entidade_tipo": "evolucao",
        "entidade_id": evolucao.id,
    }
    return EvolucaoResponse(**evolucao.__dict__)


@router.get("/pacientes/{paciente_id}/evolucoes/ultima", response_model=EvolucaoResponse)
async def buscar_ultima_devolutiva(
    paciente_id: UUID,
    request: Request,
    usuario_atual: UsuarioAutenticadoDTO = Depends(get_usuario_atual),
    use_case: BuscarUltimaDevolutivaUseCase = Depends(get_buscar_ultima_devolutiva_use_case),
) -> EvolucaoResponse:
    try:
        evolucao = await use_case.executar(
            paciente_id, usuario_atual.clinica_id, PapelUsuario(usuario_atual.papel)
        )
    except PermissaoNegadaError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except RecursoNaoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    request.state.auditoria = {
        "acao": AcaoAuditoria.VISUALIZAR,
        "entidade_tipo": "evolucao",
        "entidade_id": evolucao.id,
    }
    return EvolucaoResponse(**evolucao.__dict__)


@router.post(
    "/pacientes/{paciente_id}/evolucoes/gerar-rascunho",
    response_model=EvolucaoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def gerar_rascunho_evolucao(
    paciente_id: UUID,
    request: Request,
    arquivo: UploadFile = File(...),
    usuario_atual: UsuarioAutenticadoDTO = Depends(get_usuario_atual),
    use_case: GerarRascunhoEvolucaoUseCase = Depends(get_gerar_rascunho_evolucao_use_case),
) -> EvolucaoResponse:
    audio_bytes = await arquivo.read()
    try:
        evolucao = await use_case.executar(
            paciente_id,
            audio_bytes,
            arquivo.filename or "audio.webm",
            usuario_atual.clinica_id,
            usuario_atual.id,
            PapelUsuario(usuario_atual.papel),
        )
    except PermissaoNegadaError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except RecursoNaoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except NotImplementedError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

    request.state.auditoria = {
        "acao": AcaoAuditoria.CRIAR,
        "entidade_tipo": "evolucao",
        "entidade_id": evolucao.id,
    }
    return EvolucaoResponse(**evolucao.__dict__)


@router.patch(
    "/pacientes/{paciente_id}/evolucoes/{id}/confirmar",
    response_model=EvolucaoResponse,
)
async def confirmar_evolucao(
    paciente_id: UUID,
    id: UUID,
    body: ConfirmarEvolucaoRequest,
    request: Request,
    usuario_atual: UsuarioAutenticadoDTO = Depends(get_usuario_atual),
    use_case: ConfirmarEvolucaoUseCase = Depends(get_confirmar_evolucao_use_case),
) -> EvolucaoResponse:
    try:
        evolucao = await use_case.executar(
            id,
            ConfirmarEvolucaoInputDTO(**body.model_dump()),
            usuario_atual.clinica_id,
            PapelUsuario(usuario_atual.papel),
        )
    except PermissaoNegadaError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except RecursoNaoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    request.state.auditoria = {
        "acao": AcaoAuditoria.EDITAR,
        "entidade_tipo": "evolucao",
        "entidade_id": evolucao.id,
    }
    return EvolucaoResponse(**evolucao.__dict__)


@router.delete(
    "/pacientes/{paciente_id}/evolucoes/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def deletar_evolucao(
    paciente_id: UUID,
    id: UUID,
    request: Request,
    usuario_atual: UsuarioAutenticadoDTO = Depends(get_usuario_atual),
    use_case: DeletarEvolucaoUseCase = Depends(get_deletar_evolucao_use_case),
) -> None:
    try:
        await use_case.executar(id, usuario_atual.clinica_id, PapelUsuario(usuario_atual.papel))
    except PermissaoNegadaError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except RecursoNaoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    request.state.auditoria = {
        "acao": AcaoAuditoria.EXCLUIR,
        "entidade_tipo": "evolucao",
        "entidade_id": id,
    }
