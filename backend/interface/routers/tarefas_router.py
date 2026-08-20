from datetime import date, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status

from backend.application.dtos.auth_dto import UsuarioAutenticadoDTO
from backend.application.dtos.tarefa_dto import (
    AtualizarTarefaInputDTO,
    CriarTarefaInputDTO,
    DuplicarTarefasInputDTO,
)
from backend.application.exceptions import PermissaoNegadaError, RecursoNaoEncontradoError
from backend.application.use_cases.tarefas.atualizar_tarefa import AtualizarTarefaUseCase
from backend.application.use_cases.tarefas.criar_tarefa import CriarTarefaUseCase
from backend.application.use_cases.tarefas.deletar_tarefa import DeletarTarefaUseCase
from backend.application.use_cases.tarefas.duplicar_tarefas import DuplicarTarefasUseCase
from backend.application.use_cases.tarefas.listar_planejamento_semana import (
    ListarPlanejamentoSemanaUseCase,
)
from backend.application.use_cases.tarefas.listar_tarefas_paciente import (
    ListarTarefasPacienteUseCase,
)
from backend.application.use_cases.tarefas.marcar_conclusao_tarefa import (
    MarcarConclusaoTarefaUseCase,
)
from backend.container import (
    get_atualizar_tarefa_use_case,
    get_criar_tarefa_use_case,
    get_deletar_tarefa_use_case,
    get_duplicar_tarefas_use_case,
    get_listar_planejamento_semana_use_case,
    get_listar_tarefas_paciente_use_case,
    get_marcar_conclusao_tarefa_use_case,
)
from backend.domain.entities.log_acesso import AcaoAuditoria
from backend.domain.entities.usuario import PapelUsuario
from backend.interface.dependencies import get_usuario_atual
from backend.interface.schemas.tarefa_schema import (
    DuplicarTarefasRequest,
    MarcarConclusaoRequest,
    TarefaCreate,
    TarefaResponse,
    TarefaUpdate,
    TarefasPorPacienteResponse,
)

router = APIRouter(tags=["tarefas"])


def _semana_atual() -> tuple[date, date]:
    hoje = date.today()
    inicio = hoje - timedelta(days=hoje.weekday())
    fim = inicio + timedelta(days=6)
    return inicio, fim


@router.get("/pacientes/{paciente_id}/tarefas", response_model=list[TarefaResponse])
async def listar_tarefas_paciente(
    paciente_id: UUID,
    request: Request,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    usuario_atual: UsuarioAutenticadoDTO = Depends(get_usuario_atual),
    use_case: ListarTarefasPacienteUseCase = Depends(get_listar_tarefas_paciente_use_case),
) -> list[TarefaResponse]:
    try:
        tarefas = await use_case.executar(
            paciente_id,
            usuario_atual.clinica_id,
            PapelUsuario(usuario_atual.papel),
            data_inicio,
            data_fim,
        )
    except PermissaoNegadaError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    request.state.auditoria = {
        "acao": AcaoAuditoria.VISUALIZAR,
        "entidade_tipo": "tarefa_planejamento",
        "entidade_id": paciente_id,
    }
    return [TarefaResponse(**t.__dict__) for t in tarefas]


@router.post(
    "/pacientes/{paciente_id}/tarefas",
    response_model=TarefaResponse,
    status_code=status.HTTP_201_CREATED,
)
async def criar_tarefa(
    paciente_id: UUID,
    body: TarefaCreate,
    request: Request,
    usuario_atual: UsuarioAutenticadoDTO = Depends(get_usuario_atual),
    use_case: CriarTarefaUseCase = Depends(get_criar_tarefa_use_case),
) -> TarefaResponse:
    try:
        tarefa = await use_case.executar(
            paciente_id,
            CriarTarefaInputDTO(**body.model_dump()),
            usuario_atual.clinica_id,
            PapelUsuario(usuario_atual.papel),
        )
    except PermissaoNegadaError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except RecursoNaoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    request.state.auditoria = {
        "acao": AcaoAuditoria.CRIAR,
        "entidade_tipo": "tarefa_planejamento",
        "entidade_id": tarefa.id,
    }
    return TarefaResponse(**tarefa.__dict__)


@router.patch("/pacientes/{paciente_id}/tarefas/{id}", response_model=TarefaResponse)
async def atualizar_tarefa(
    paciente_id: UUID,
    id: UUID,
    body: TarefaUpdate,
    request: Request,
    usuario_atual: UsuarioAutenticadoDTO = Depends(get_usuario_atual),
    use_case: AtualizarTarefaUseCase = Depends(get_atualizar_tarefa_use_case),
) -> TarefaResponse:
    try:
        tarefa = await use_case.executar(
            id,
            AtualizarTarefaInputDTO(**body.model_dump()),
            usuario_atual.clinica_id,
            PapelUsuario(usuario_atual.papel),
        )
    except PermissaoNegadaError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except RecursoNaoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    request.state.auditoria = {
        "acao": AcaoAuditoria.EDITAR,
        "entidade_tipo": "tarefa_planejamento",
        "entidade_id": tarefa.id,
    }
    return TarefaResponse(**tarefa.__dict__)


@router.patch("/pacientes/{paciente_id}/tarefas/{id}/concluir", response_model=TarefaResponse)
async def marcar_conclusao_tarefa(
    paciente_id: UUID,
    id: UUID,
    body: MarcarConclusaoRequest,
    request: Request,
    usuario_atual: UsuarioAutenticadoDTO = Depends(get_usuario_atual),
    use_case: MarcarConclusaoTarefaUseCase = Depends(get_marcar_conclusao_tarefa_use_case),
) -> TarefaResponse:
    try:
        tarefa = await use_case.executar(
            id,
            body.concluido,
            usuario_atual.clinica_id,
            PapelUsuario(usuario_atual.papel),
        )
    except PermissaoNegadaError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except RecursoNaoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    request.state.auditoria = {
        "acao": AcaoAuditoria.EDITAR,
        "entidade_tipo": "tarefa_planejamento",
        "entidade_id": tarefa.id,
    }
    return TarefaResponse(**tarefa.__dict__)


@router.post(
    "/pacientes/{paciente_id}/tarefas/duplicar",
    response_model=list[TarefaResponse],
    status_code=status.HTTP_201_CREATED,
)
async def duplicar_tarefas(
    paciente_id: UUID,
    body: DuplicarTarefasRequest,
    request: Request,
    usuario_atual: UsuarioAutenticadoDTO = Depends(get_usuario_atual),
    use_case: DuplicarTarefasUseCase = Depends(get_duplicar_tarefas_use_case),
) -> list[TarefaResponse]:
    try:
        tarefas = await use_case.executar(
            paciente_id,
            DuplicarTarefasInputDTO(**body.model_dump()),
            usuario_atual.clinica_id,
            PapelUsuario(usuario_atual.papel),
        )
    except PermissaoNegadaError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except RecursoNaoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    request.state.auditoria = [
        {
            "acao": AcaoAuditoria.CRIAR,
            "entidade_tipo": "tarefa_planejamento",
            "entidade_id": t.id,
        }
        for t in tarefas
    ]
    return [TarefaResponse(**t.__dict__) for t in tarefas]


@router.delete(
    "/pacientes/{paciente_id}/tarefas/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def deletar_tarefa(
    paciente_id: UUID,
    id: UUID,
    request: Request,
    usuario_atual: UsuarioAutenticadoDTO = Depends(get_usuario_atual),
    use_case: DeletarTarefaUseCase = Depends(get_deletar_tarefa_use_case),
) -> None:
    try:
        await use_case.executar(id, usuario_atual.clinica_id, PapelUsuario(usuario_atual.papel))
    except PermissaoNegadaError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except RecursoNaoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    request.state.auditoria = {
        "acao": AcaoAuditoria.EXCLUIR,
        "entidade_tipo": "tarefa_planejamento",
        "entidade_id": id,
    }


@router.get("/planejamento/semana", response_model=list[TarefasPorPacienteResponse])
async def listar_planejamento_semana(
    request: Request,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    usuario_atual: UsuarioAutenticadoDTO = Depends(get_usuario_atual),
    use_case: ListarPlanejamentoSemanaUseCase = Depends(get_listar_planejamento_semana_use_case),
) -> list[TarefasPorPacienteResponse]:
    if data_inicio is None or data_fim is None:
        data_inicio, data_fim = _semana_atual()

    try:
        cards = await use_case.executar(
            usuario_atual.clinica_id,
            PapelUsuario(usuario_atual.papel),
            data_inicio,
            data_fim,
        )
    except PermissaoNegadaError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    request.state.auditoria = [
        {
            "acao": AcaoAuditoria.VISUALIZAR,
            "entidade_tipo": "tarefa_planejamento",
            "entidade_id": card.paciente_id,
        }
        for card in cards
    ]
    return [
        TarefasPorPacienteResponse(
            paciente_id=card.paciente_id,
            paciente_nome=card.paciente_nome,
            tarefas=[TarefaResponse(**t.__dict__) for t in card.tarefas],
        )
        for card in cards
    ]
