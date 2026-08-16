from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status

from backend.application.dtos.auth_dto import UsuarioAutenticadoDTO
from backend.application.dtos.paciente_dto import (
    AtualizarPacienteInputDTO,
    CriarPacienteInputDTO,
    PacienteDTO,
)
from backend.application.exceptions import PermissaoNegadaError, RecursoNaoEncontradoError
from backend.application.use_cases.pacientes.atualizar_paciente import AtualizarPacienteUseCase
from backend.application.use_cases.pacientes.atualizar_status_paciente import (
    AtualizarStatusPacienteUseCase,
)
from backend.application.use_cases.pacientes.buscar_paciente import BuscarPacienteUseCase
from backend.application.use_cases.pacientes.criar_paciente import CriarPacienteUseCase
from backend.application.use_cases.pacientes.deletar_paciente import DeletarPacienteUseCase
from backend.application.use_cases.pacientes.listar_pacientes import ListarPacientesUseCase
from backend.container import (
    get_atualizar_paciente_use_case,
    get_atualizar_status_paciente_use_case,
    get_buscar_paciente_use_case,
    get_criar_paciente_use_case,
    get_deletar_paciente_use_case,
    get_listar_pacientes_use_case,
)
from backend.domain.authorization.policy import Recurso, usuario_pode
from backend.domain.entities.log_acesso import AcaoAuditoria
from backend.domain.entities.usuario import PapelUsuario
from backend.interface.dependencies import get_usuario_atual
from backend.interface.schemas.paciente_schema import (
    PacienteCreate,
    PacienteResponse,
    PacienteResponseCadastral,
    PacienteStatusUpdate,
    PacienteUpdate,
)

router = APIRouter(prefix="/pacientes", tags=["pacientes"])


_CAMPOS_CADASTRAIS = (
    "id",
    "clinica_id",
    "nome_completo",
    "data_nascimento",
    "nome_mae",
    "nome_pai",
    "tem_irmaos",
    "status",
    "nome_irmaos",
    "consentimento_lgpd_assinado_em",
    "idade",
    "observacoes",
    "criado_em",
    "atualizado_em",
)


def _serializar(dto: PacienteDTO, papel: str) -> PacienteResponse | PacienteResponseCadastral:
    cadastrais = {campo: getattr(dto, campo) for campo in _CAMPOS_CADASTRAIS}
    if usuario_pode(PapelUsuario(papel), Recurso.PACIENTE_CLINICO):
        return PacienteResponse(
            **cadastrais,
            diagnostico=dto.diagnostico,
            data_inicio=dto.data_inicio,
            faz_uso_medicamento=dto.faz_uso_medicamento,
            informacoes_nascimento=dto.informacoes_nascimento,
            queixa_principal=dto.queixa_principal,
        )
    return PacienteResponseCadastral(**cadastrais)


@router.get("", response_model=list[PacienteResponse] | list[PacienteResponseCadastral])
async def listar_pacientes(
    request: Request,
    usuario_atual: UsuarioAutenticadoDTO = Depends(get_usuario_atual),
    use_case: ListarPacientesUseCase = Depends(get_listar_pacientes_use_case),
) -> list[PacienteResponse | PacienteResponseCadastral]:
    pacientes = await use_case.executar(usuario_atual.clinica_id)

    if pacientes:
        request.state.auditoria = [
            {
                "acao": AcaoAuditoria.VISUALIZAR,
                "entidade_tipo": "paciente",
                "entidade_id": p.id,
            }
            for p in pacientes
        ]
    return [_serializar(p, usuario_atual.papel) for p in pacientes]


@router.post("", response_model=PacienteResponse | PacienteResponseCadastral, status_code=status.HTTP_201_CREATED)
async def criar_paciente(
    body: PacienteCreate,
    usuario_atual: UsuarioAutenticadoDTO = Depends(get_usuario_atual),
    use_case: CriarPacienteUseCase = Depends(get_criar_paciente_use_case),
) -> PacienteResponse | PacienteResponseCadastral:
    try:
        paciente = await use_case.executar(
            CriarPacienteInputDTO(**body.model_dump()),
            usuario_atual.clinica_id,
            PapelUsuario(usuario_atual.papel),
        )
    except PermissaoNegadaError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    return _serializar(paciente, usuario_atual.papel)


@router.get("/{id}", response_model=PacienteResponse | PacienteResponseCadastral)
async def buscar_paciente(
    id: UUID,
    request: Request,
    usuario_atual: UsuarioAutenticadoDTO = Depends(get_usuario_atual),
    use_case: BuscarPacienteUseCase = Depends(get_buscar_paciente_use_case),
) -> PacienteResponse | PacienteResponseCadastral:
    try:
        paciente = await use_case.executar(id, usuario_atual.clinica_id)
    except RecursoNaoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    request.state.auditoria = {
        "acao": AcaoAuditoria.VISUALIZAR,
        "entidade_tipo": "paciente",
        "entidade_id": id,
    }
    return _serializar(paciente, usuario_atual.papel)


@router.put("/{id}", response_model=PacienteResponse | PacienteResponseCadastral)
async def atualizar_paciente(
    id: UUID,
    body: PacienteUpdate,
    request: Request,
    usuario_atual: UsuarioAutenticadoDTO = Depends(get_usuario_atual),
    use_case: AtualizarPacienteUseCase = Depends(get_atualizar_paciente_use_case),
) -> PacienteResponse | PacienteResponseCadastral:
    try:
        paciente = await use_case.executar(
            id,
            AtualizarPacienteInputDTO(**body.model_dump()),
            usuario_atual.clinica_id,
            PapelUsuario(usuario_atual.papel),
        )
    except PermissaoNegadaError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except RecursoNaoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    request.state.auditoria = {
        "acao": AcaoAuditoria.EDITAR,
        "entidade_tipo": "paciente",
        "entidade_id": id,
    }
    return _serializar(paciente, usuario_atual.papel)


@router.patch("/{id}/status", response_model=PacienteResponse | PacienteResponseCadastral)
async def atualizar_status_paciente(
    id: UUID,
    body: PacienteStatusUpdate,
    usuario_atual: UsuarioAutenticadoDTO = Depends(get_usuario_atual),
    use_case: AtualizarStatusPacienteUseCase = Depends(get_atualizar_status_paciente_use_case),
) -> PacienteResponse | PacienteResponseCadastral:
    try:
        paciente = await use_case.executar(id, body.status, usuario_atual.clinica_id)
    except RecursoNaoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    return _serializar(paciente, usuario_atual.papel)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_paciente(
    id: UUID,
    request: Request,
    usuario_atual: UsuarioAutenticadoDTO = Depends(get_usuario_atual),
    use_case: DeletarPacienteUseCase = Depends(get_deletar_paciente_use_case),
) -> None:
    try:
        await use_case.executar(id, usuario_atual.clinica_id, PapelUsuario(usuario_atual.papel))
    except PermissaoNegadaError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except RecursoNaoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    request.state.auditoria = {
        "acao": AcaoAuditoria.EXCLUIR,
        "entidade_tipo": "paciente",
        "entidade_id": id,
    }
