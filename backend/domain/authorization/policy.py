from enum import Enum

from backend.domain.entities.usuario import PapelUsuario


class Recurso(Enum):
    PACIENTE_CADASTRO = "paciente_cadastro"
    PACIENTE_CLINICO = "paciente_clinico"
    EVOLUCAO = "evolucao"
    ANEXO_CLINICO = "anexo_clinico"
    ANEXO_NAO_CLINICO = "anexo_nao_clinico"
    USUARIOS = "usuarios"
    LOGS_AUDITORIA = "logs_auditoria"


_MATRIZ_PERMISSOES: dict[Recurso, set[PapelUsuario]] = {
    Recurso.PACIENTE_CADASTRO: {PapelUsuario.ADMIN, PapelUsuario.FONO, PapelUsuario.SECRETARIA},
    Recurso.PACIENTE_CLINICO: {PapelUsuario.ADMIN, PapelUsuario.FONO},
    Recurso.EVOLUCAO: {PapelUsuario.ADMIN, PapelUsuario.FONO},
    Recurso.ANEXO_CLINICO: {PapelUsuario.ADMIN, PapelUsuario.FONO},
    Recurso.ANEXO_NAO_CLINICO: {PapelUsuario.ADMIN, PapelUsuario.FONO, PapelUsuario.SECRETARIA},
    Recurso.USUARIOS: {PapelUsuario.ADMIN},
    Recurso.LOGS_AUDITORIA: {PapelUsuario.ADMIN},
}


def usuario_pode(papel: PapelUsuario, recurso: Recurso) -> bool:
    """Unica fonte de verdade de RBAC - ver tabela em docs/seguranca.md.

    Nunca fazer `if papel == "admin"` solto em router: sempre passar por aqui.
    """
    return papel in _MATRIZ_PERMISSOES.get(recurso, set())
