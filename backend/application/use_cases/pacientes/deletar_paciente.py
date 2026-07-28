from uuid import UUID

from backend.application.exceptions import PermissaoNegadaError, RecursoNaoEncontradoError
from backend.domain.authorization.policy import Recurso, usuario_pode
from backend.domain.entities.usuario import PapelUsuario
from backend.domain.repositories.paciente_repository import PacienteRepository


class DeletarPacienteUseCase:
    def __init__(self, paciente_repository: PacienteRepository) -> None:
        self._paciente_repository = paciente_repository

    async def executar(self, id: UUID, clinica_id: UUID, papel: PapelUsuario) -> None:
        if not usuario_pode(papel, Recurso.PACIENTE_CADASTRO):
            raise PermissaoNegadaError("Papel sem permissao para excluir paciente")

        paciente = await self._paciente_repository.buscar_por_id(id, clinica_id)
        if paciente is None:
            raise RecursoNaoEncontradoError("Paciente nao encontrado")

        await self._paciente_repository.soft_delete(id, clinica_id)
