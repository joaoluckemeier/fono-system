from enum import Enum

from backend.domain.entities.anexo import EntidadeAnexavel
from backend.domain.entities.usuario import PapelUsuario


class Recurso(Enum):
    PACIENTE_CADASTRO = "paciente_cadastro"
    PACIENTE_CLINICO = "paciente_clinico"
    EVOLUCAO = "evolucao"
    ANEXO_CLINICO = "anexo_clinico"
    ANEXO_NAO_CLINICO = "anexo_nao_clinico"
    USUARIOS = "usuarios"
    LOGS_AUDITORIA = "logs_auditoria"
    TERMO_MODELO = "termo_modelo"
    TERMO_GERACAO = "termo_geracao"
    PLANEJAMENTO_TERAPEUTICO = "planejamento_terapeutico"


_MATRIZ_PERMISSOES: dict[Recurso, set[PapelUsuario]] = {
    Recurso.PACIENTE_CADASTRO: {PapelUsuario.ADMIN, PapelUsuario.FONO, PapelUsuario.SECRETARIA},
    Recurso.PACIENTE_CLINICO: {PapelUsuario.ADMIN, PapelUsuario.FONO},
    Recurso.EVOLUCAO: {PapelUsuario.ADMIN, PapelUsuario.FONO},
    Recurso.ANEXO_CLINICO: {PapelUsuario.ADMIN, PapelUsuario.FONO},
    Recurso.ANEXO_NAO_CLINICO: {PapelUsuario.ADMIN, PapelUsuario.FONO, PapelUsuario.SECRETARIA},
    Recurso.USUARIOS: {PapelUsuario.ADMIN},
    Recurso.LOGS_AUDITORIA: {PapelUsuario.ADMIN},
    Recurso.TERMO_MODELO: {PapelUsuario.ADMIN},
    Recurso.TERMO_GERACAO: {PapelUsuario.ADMIN, PapelUsuario.FONO},
    Recurso.PLANEJAMENTO_TERAPEUTICO: {PapelUsuario.ADMIN, PapelUsuario.FONO},
}


def usuario_pode(papel: PapelUsuario, recurso: Recurso) -> bool:
    """Unica fonte de verdade de RBAC - ver tabela em docs/seguranca.md.

    Nunca fazer `if papel == "admin"` solto em router: sempre passar por aqui.
    """
    return papel in _MATRIZ_PERMISSOES.get(recurso, set())


RECURSO_POR_ENTIDADE_ANEXO: dict[EntidadeAnexavel, Recurso] = {
    EntidadeAnexavel.EVOLUCAO: Recurso.ANEXO_CLINICO,
    EntidadeAnexavel.PACIENTE: Recurso.ANEXO_NAO_CLINICO,
    EntidadeAnexavel.PROTOCOLO_PACIENTE: Recurso.ANEXO_NAO_CLINICO,
}
