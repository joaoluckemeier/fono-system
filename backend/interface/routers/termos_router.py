from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from backend.application.dtos.auth_dto import UsuarioAutenticadoDTO
from backend.application.dtos.termo_gerado_dto import GerarTermoInputDTO
from backend.application.exceptions import PermissaoNegadaError, RecursoNaoEncontradoError
from backend.application.use_cases.termos.gerar_termo import GerarTermoUseCase
from backend.application.use_cases.termos.listar_termos_gerados import ListarTermosGeradosUseCase
from backend.container import get_gerar_termo_use_case, get_listar_termos_gerados_use_case
from backend.domain.entities.log_acesso import AcaoAuditoria
from backend.domain.entities.usuario import PapelUsuario
from backend.interface.dependencies import get_usuario_atual
from backend.interface.schemas.termo_gerado_schema import TermoGerarRequest, TermoGeradoResponse

router = APIRouter(tags=["termos"])


@router.post("/pacientes/{paciente_id}/termos")
async def gerar_termo(
    paciente_id: UUID,
    body: TermoGerarRequest,
    request: Request,
    usuario_atual: UsuarioAutenticadoDTO = Depends(get_usuario_atual),
    use_case: GerarTermoUseCase = Depends(get_gerar_termo_use_case),
) -> Response:
    try:
        resultado = await use_case.executar(
            paciente_id,
            GerarTermoInputDTO(modelo_id=body.modelo_id),
            usuario_atual.clinica_id,
            usuario_atual.id,
            usuario_atual.nome,
            PapelUsuario(usuario_atual.papel),
        )
    except PermissaoNegadaError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except RecursoNaoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    request.state.auditoria = {
        "acao": AcaoAuditoria.EXPORTAR,
        "entidade_tipo": "termo_gerado",
        "entidade_id": resultado.termo.id,
    }
    return Response(content=resultado.pdf_bytes, media_type="application/pdf")


@router.get("/pacientes/{paciente_id}/termos", response_model=list[TermoGeradoResponse])
async def listar_termos_gerados(
    paciente_id: UUID,
    request: Request,
    usuario_atual: UsuarioAutenticadoDTO = Depends(get_usuario_atual),
    use_case: ListarTermosGeradosUseCase = Depends(get_listar_termos_gerados_use_case),
) -> list[TermoGeradoResponse]:
    try:
        termos = await use_case.executar(
            paciente_id, usuario_atual.clinica_id, PapelUsuario(usuario_atual.papel)
        )
    except PermissaoNegadaError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    if termos:
        request.state.auditoria = [
            {
                "acao": AcaoAuditoria.VISUALIZAR,
                "entidade_tipo": "termo_gerado",
                "entidade_id": t.id,
            }
            for t in termos
        ]
    return [TermoGeradoResponse(**t.__dict__) for t in termos]
