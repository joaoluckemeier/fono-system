from datetime import UTC, date, datetime
from uuid import uuid4

from backend.application.use_cases.tarefas.listar_planejamento_semana import (
    ListarPlanejamentoSemanaUseCase,
)
from backend.domain.entities.paciente import Paciente
from backend.domain.entities.tarefa import Tarefa
from backend.domain.entities.usuario import PapelUsuario
from tests.unit.fakes import FakePacienteRepository, FakeTarefaRepository


def _paciente(clinica_id, nome: str) -> Paciente:
    agora = datetime.now(UTC)
    return Paciente(
        id=uuid4(),
        clinica_id=clinica_id,
        criado_em=agora,
        atualizado_em=agora,
        deletado=False,
        deletado_em=None,
        nome_completo=nome,
        data_nascimento=date(2018, 5, 10),
        nome_mae="Maria",
        nome_pai="Pedro",
        tem_irmaos=False,
        faz_uso_medicamento="nao",
    )


def _tarefa(clinica_id, paciente_id, data: date, titulo: str) -> Tarefa:
    agora = datetime.now(UTC)
    return Tarefa(
        id=uuid4(),
        clinica_id=clinica_id,
        criado_em=agora,
        atualizado_em=agora,
        deletado=False,
        deletado_em=None,
        paciente_id=paciente_id,
        data=data,
        titulo=titulo,
    )


async def test_agrupa_tarefas_por_paciente_no_periodo():
    clinica_id = uuid4()
    paciente_repository = FakePacienteRepository()
    tarefa_repository = FakeTarefaRepository()

    paciente_a = await paciente_repository.salvar(_paciente(clinica_id, "Paciente A"))
    paciente_b = await paciente_repository.salvar(_paciente(clinica_id, "Paciente B"))
    paciente_c = await paciente_repository.salvar(_paciente(clinica_id, "Paciente C - fora do periodo"))

    inicio, fim = date(2026, 1, 5), date(2026, 1, 11)
    await tarefa_repository.salvar(_tarefa(clinica_id, paciente_a.id, date(2026, 1, 6), "T1"))
    await tarefa_repository.salvar(_tarefa(clinica_id, paciente_a.id, date(2026, 1, 7), "T2"))
    await tarefa_repository.salvar(_tarefa(clinica_id, paciente_b.id, date(2026, 1, 8), "T3"))
    await tarefa_repository.salvar(_tarefa(clinica_id, paciente_c.id, date(2026, 1, 20), "Fora"))

    cards = await ListarPlanejamentoSemanaUseCase(tarefa_repository, paciente_repository).executar(
        clinica_id, PapelUsuario.FONO, inicio, fim
    )

    assert len(cards) == 2
    por_paciente = {c.paciente_id: c for c in cards}
    assert len(por_paciente[paciente_a.id].tarefas) == 2
    assert len(por_paciente[paciente_b.id].tarefas) == 1
    assert paciente_c.id not in por_paciente
