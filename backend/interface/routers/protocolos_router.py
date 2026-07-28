from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from backend.application.dtos.auth_dto import UsuarioAutenticadoDTO
from backend.application.dtos.protocolo_dto import CriarProtocoloInputDTO
from backend.application.dtos.protocolo_paciente_dto import (
    AtualizarStatusProtocoloPacienteInputDTO,
    CriarProtocoloPacienteInputDTO,
)
from backend.application.exceptions import RecursoNaoEncontradoError
from backend.application.use_cases.protocolos.associar_protocolo_paciente import (
    AssociarProtocoloPacienteUseCase,
)
from backend.application.use_cases.protocolos.atualizar_status_protocolo_paciente import (
    AtualizarStatusProtocoloPacienteUseCase,
)
from backend.application.use_cases.protocolos.criar_protocolo import CriarProtocoloUseCase
from backend.application.use_cases.protocolos.deletar_protocolo_paciente import (
    DeletarProtocoloPacienteUseCase,
)
from backend.application.use_cases.protocolos.listar_protocolos import ListarProtocolosUseCase
from backend.application.use_cases.protocolos.listar_protocolos_paciente import (
    ListarProtocolosPacienteUseCase,
)
from backend.container import (
    get_associar_protocolo_paciente_use_case,
    get_atualizar_status_protocolo_paciente_use_case,
    get_criar_protocolo_use_case,
    get_deletar_protocolo_paciente_use_case,
    get_listar_protocolos_paciente_use_case,
    get_listar_protocolos_use_case,
)
from backend.interface.dependencies import get_usuario_atual
from backend.interface.schemas.protocolo_schema import (
    ProtocoloCreate,
    ProtocoloPacienteCreate,
    ProtocoloPacienteResponse,
    ProtocoloPacienteStatusUpdate,
    ProtocoloResponse,
)

router = APIRouter(tags=["protocolos"])


@router.get("/protocolos", response_model=list[ProtocoloResponse])
async def listar_protocolos(
    usuario_atual: UsuarioAutenticadoDTO = Depends(get_usuario_atual),
    use_case: ListarProtocolosUseCase = Depends(get_listar_protocolos_use_case),
) -> list[ProtocoloResponse]:
    protocolos = await use_case.executar(usuario_atual.clinica_id)
    return [ProtocoloResponse(**p.__dict__) for p in protocolos]


@router.post("/protocolos", response_model=ProtocoloResponse, status_code=status.HTTP_201_CREATED)
async def criar_protocolo(
    body: ProtocoloCreate,
    usuario_atual: UsuarioAutenticadoDTO = Depends(get_usuario_atual),
    use_case: CriarProtocoloUseCase = Depends(get_criar_protocolo_use_case),
) -> ProtocoloResponse:
    protocolo = await use_case.executar(
        CriarProtocoloInputDTO(**body.model_dump()), usuario_atual.clinica_id
    )
    return ProtocoloResponse(**protocolo.__dict__)


@router.get(
    "/pacientes/{paciente_id}/protocolos", response_model=list[ProtocoloPacienteResponse]
)
async def listar_protocolos_paciente(
    paciente_id: UUID,
    usuario_atual: UsuarioAutenticadoDTO = Depends(get_usuario_atual),
    use_case: ListarProtocolosPacienteUseCase = Depends(get_listar_protocolos_paciente_use_case),
) -> list[ProtocoloPacienteResponse]:
    registros = await use_case.executar(paciente_id, usuario_atual.clinica_id)
    return [ProtocoloPacienteResponse(**r.__dict__) for r in registros]


@router.post(
    "/pacientes/{paciente_id}/protocolos",
    response_model=ProtocoloPacienteResponse,
    status_code=status.HTTP_201_CREATED,
)
async def associar_protocolo_paciente(
    paciente_id: UUID,
    body: ProtocoloPacienteCreate,
    usuario_atual: UsuarioAutenticadoDTO = Depends(get_usuario_atual),
    use_case: AssociarProtocoloPacienteUseCase = Depends(get_associar_protocolo_paciente_use_case),
) -> ProtocoloPacienteResponse:
    try:
        registro = await use_case.executar(
            paciente_id, CriarProtocoloPacienteInputDTO(**body.model_dump()), usuario_atual.clinica_id
        )
    except RecursoNaoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    return ProtocoloPacienteResponse(**registro.__dict__)


@router.delete("/pacientes/{paciente_id}/protocolos/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_protocolo_paciente(
    paciente_id: UUID,
    id: UUID,
    usuario_atual: UsuarioAutenticadoDTO = Depends(get_usuario_atual),
    use_case: DeletarProtocoloPacienteUseCase = Depends(get_deletar_protocolo_paciente_use_case),
) -> None:
    try:
        await use_case.executar(id, usuario_atual.clinica_id)
    except RecursoNaoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch(
    "/pacientes/{paciente_id}/protocolos/{id}",
    response_model=ProtocoloPacienteResponse,
)
async def atualizar_status_protocolo_paciente(
    paciente_id: UUID,
    id: UUID,
    body: ProtocoloPacienteStatusUpdate,
    usuario_atual: UsuarioAutenticadoDTO = Depends(get_usuario_atual),
    use_case: AtualizarStatusProtocoloPacienteUseCase = Depends(
        get_atualizar_status_protocolo_paciente_use_case
    ),
) -> ProtocoloPacienteResponse:
    try:
        registro = await use_case.executar(
            id,
            AtualizarStatusProtocoloPacienteInputDTO(**body.model_dump()),
            usuario_atual.clinica_id,
        )
    except RecursoNaoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    return ProtocoloPacienteResponse(**registro.__dict__)
