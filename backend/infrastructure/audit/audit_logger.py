from datetime import UTC, datetime
from uuid import UUID, uuid4

from backend.domain.entities.log_acesso import AcaoAuditoria, LogAcesso
from backend.domain.repositories.log_acesso_repository import LogAcessoRepository


class AuditLogger:
    """Grava logs_acesso - leitura E escrita de dado clinico sensivel (paciente, evolucao)."""

    def __init__(self, log_acesso_repository: LogAcessoRepository) -> None:
        self._log_acesso_repository = log_acesso_repository

    async def registrar(
        self,
        clinica_id: UUID,
        usuario_id: UUID,
        acao: AcaoAuditoria,
        entidade_tipo: str,
        entidade_id: UUID,
        ip_origem: str,
    ) -> None:
        agora = datetime.now(UTC)
        await self._log_acesso_repository.salvar(
            LogAcesso(
                id=uuid4(),
                clinica_id=clinica_id,
                criado_em=agora,
                atualizado_em=agora,
                deletado=False,
                deletado_em=None,
                usuario_id=usuario_id,
                acao=acao,
                entidade_tipo=entidade_tipo,
                entidade_id=entidade_id,
                ip_origem=ip_origem,
            )
        )
