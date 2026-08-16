from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum

from backend.domain.entities.base import EntidadeBase


class StatusPaciente(Enum):
    EM_AVALIACAO = "em_avaliacao"
    EM_ACOMPANHAMENTO = "em_acompanhamento"
    ALTA = "alta"


@dataclass
class Paciente(EntidadeBase):
    nome_completo: str
    data_nascimento: date
    nome_mae: str
    nome_pai: str
    tem_irmaos: bool
    faz_uso_medicamento: str
    status: StatusPaciente = StatusPaciente.EM_AVALIACAO
    nome_irmaos: str | None = None
    diagnostico: str | None = None
    data_inicio: date | None = None
    consentimento_lgpd_assinado_em: datetime | None = None
    informacoes_nascimento: str | None = None
    queixa_principal: str | None = None
    observacoes: str | None = None

    def tem_consentimento_lgpd(self) -> bool:
        return self.consentimento_lgpd_assinado_em is not None

    @property
    def idade(self) -> int:
        hoje = date.today()
        anos = hoje.year - self.data_nascimento.year
        if (hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day):
            anos -= 1
        return anos
