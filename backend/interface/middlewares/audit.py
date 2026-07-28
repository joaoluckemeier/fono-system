import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from backend.infrastructure.audit.audit_logger import AuditLogger
from backend.infrastructure.database.connection import async_session_factory
from backend.infrastructure.repositories.log_acesso_repository import LogAcessoRepositoryImpl

logger = structlog.get_logger()


class AuditMiddleware(BaseHTTPMiddleware):
    """Grava logs_acesso automaticamente quando o endpoint marca a requisicao como sensivel.

    Um router de dado clinico (paciente, evolucao) define, apos autenticar o usuario:
        request.state.auditoria = {
            "acao": AcaoAuditoria.VISUALIZAR, "entidade_tipo": "paciente", "entidade_id": id,
        }
    e este middleware persiste o registro depois que a resposta e computada, sem o router
    precisar conhecer AuditLogger diretamente.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)

        auditoria = getattr(request.state, "auditoria", None)
        usuario_atual = getattr(request.state, "usuario_atual", None)
        if auditoria is None or usuario_atual is None:
            return response

        try:
            async with async_session_factory() as session:
                audit_logger = AuditLogger(LogAcessoRepositoryImpl(session))
                await audit_logger.registrar(
                    clinica_id=usuario_atual.clinica_id,
                    usuario_id=usuario_atual.id,
                    acao=auditoria["acao"],
                    entidade_tipo=auditoria["entidade_tipo"],
                    entidade_id=auditoria["entidade_id"],
                    ip_origem=request.client.host if request.client else "desconhecido",
                )
        except Exception:
            logger.exception("falha_ao_gravar_log_acesso")

        return response
