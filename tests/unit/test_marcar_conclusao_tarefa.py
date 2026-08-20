from datetime import UTC, date, datetime
from uuid import uuid4

from backend.application.use_cases.tarefas.marcar_conclusao_tarefa import (
    MarcarConclusaoTarefaUseCase,
)
from backend.domain.entities.tarefa import Tarefa
from backend.domain.entities.usuario import PapelUsuario
from tests.unit.fakes import FakeTarefaRepository


async def _tarefa_para_teste(tarefa_repository: FakeTarefaRepository, clinica_id) -> Tarefa:
    agora = datetime.now(UTC)
    tarefa = Tarefa(
        id=uuid4(),
        clinica_id=clinica_id,
        criado_em=agora,
        atualizado_em=agora,
        deletado=False,
        deletado_em=None,
        paciente_id=uuid4(),
        data=date(2026, 1, 5),
        titulo="Exercicio de sopro",
    )
    return await tarefa_repository.salvar(tarefa)


async def test_marcar_concluido_seta_timestamp():
    clinica_id = uuid4()
    repository = FakeTarefaRepository()
    tarefa = await _tarefa_para_teste(repository, clinica_id)

    resultado = await MarcarConclusaoTarefaUseCase(repository).executar(
        tarefa.id, True, clinica_id, PapelUsuario.FONO
    )

    assert resultado.concluido is True
    assert resultado.concluido_em is not None


async def test_desmarcar_limpa_timestamp():
    clinica_id = uuid4()
    repository = FakeTarefaRepository()
    tarefa = await _tarefa_para_teste(repository, clinica_id)

    use_case = MarcarConclusaoTarefaUseCase(repository)
    await use_case.executar(tarefa.id, True, clinica_id, PapelUsuario.FONO)
    resultado = await use_case.executar(tarefa.id, False, clinica_id, PapelUsuario.FONO)

    assert resultado.concluido is False
    assert resultado.concluido_em is None
