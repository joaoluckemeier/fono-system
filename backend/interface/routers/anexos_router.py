from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status

from backend.application.dtos.anexo_dto import CriarAnexoInputDTO
from backend.application.dtos.auth_dto import UsuarioAutenticadoDTO
from backend.application.exceptions import PermissaoNegadaError, RecursoNaoEncontradoError
from backend.application.use_cases.anexos.criar_anexo import CriarAnexoUseCase
from backend.application.use_cases.anexos.deletar_anexo import DeletarAnexoUseCase
from backend.application.use_cases.anexos.listar_anexos import ListarAnexosUseCase
from backend.container import (
    get_criar_anexo_use_case,
    get_deletar_anexo_use_case,
    get_listar_anexos_use_case,
)
from backend.domain.entities.anexo import EntidadeAnexavel
from backend.domain.entities.log_acesso import AcaoAuditoria
from backend.domain.entities.usuario import PapelUsuario
from backend.interface.dependencies import get_usuario_atual
from backend.interface.schemas.anexo_schema import AnexoResponse

router = APIRouter(prefix="/anexos", tags=["anexos"])


@router.get("", response_model=list[AnexoResponse])
async def listar_anexos(
    request: Request,
    entidade_tipo: str,
    entidade_id: UUID,
    usuario_atual: UsuarioAutenticadoDTO = Depends(get_usuario_atual),
    use_case: ListarAnexosUseCase = Depends(get_listar_anexos_use_case),
) -> list[AnexoResponse]:
    try:
        anexos = await use_case.executar(
            entidade_tipo, entidade_id, usuario_atual.clinica_id, PapelUsuario(usuario_atual.papel)
        )
    except PermissaoNegadaError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    if anexos:
        request.state.auditoria = [
            {
                "acao": AcaoAuditoria.VISUALIZAR,
                "entidade_tipo": "anexo",
                "entidade_id": a.id,
            }
            for a in anexos
        ]
    return [AnexoResponse(**a.__dict__) for a in anexos]


@router.post("", response_model=AnexoResponse, status_code=status.HTTP_201_CREATED)
async def criar_anexo(
    request: Request,
    entidade_tipo: str = Form(...),
    entidade_id: UUID = Form(...),
    tipo_arquivo: str = Form(...),
    arquivo: UploadFile = File(...),
    usuario_atual: UsuarioAutenticadoDTO = Depends(get_usuario_atual),
    use_case: CriarAnexoUseCase = Depends(get_criar_anexo_use_case),
) -> AnexoResponse:
    conteudo = await arquivo.read()
    try:
        anexo = await use_case.executar(
            CriarAnexoInputDTO(
                entidade_tipo=entidade_tipo,
                entidade_id=entidade_id,
                tipo_arquivo=tipo_arquivo,
                nome_arquivo=arquivo.filename or "arquivo",
                conteudo=conteudo,
            ),
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

    if anexo.entidade_tipo == EntidadeAnexavel.EVOLUCAO.value:
        request.state.auditoria = {
            "acao": AcaoAuditoria.CRIAR,
            "entidade_tipo": "anexo",
            "entidade_id": anexo.id,
        }
    return AnexoResponse(**anexo.__dict__)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_anexo(
    id: UUID,
    usuario_atual: UsuarioAutenticadoDTO = Depends(get_usuario_atual),
    use_case: DeletarAnexoUseCase = Depends(get_deletar_anexo_use_case),
) -> None:
    try:
        await use_case.executar(id, usuario_atual.clinica_id, PapelUsuario(usuario_atual.papel))
    except PermissaoNegadaError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except RecursoNaoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
