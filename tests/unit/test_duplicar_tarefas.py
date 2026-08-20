from datetime import UTC, date, datetime
from uuid import uuid4

from backend.application.dtos.tarefa_dto import DuplicarTarefasInputDTO
from backend.application.use_cases.tarefas.duplicar_tarefas import DuplicarTarefasUseCase
from backend.domain.entities.tarefa import PrioridadeTarefa, Tarefa
from backend.domain.entities.usuario import PapelUsuario
from tests.unit.fakes import FakeTarefaRepository


def _tarefa(clinica_id, paciente_id, titulo: str, concluido: bool = False) -> Tarefa:
    agora = datetime.now(UTC)
    return Tarefa(
        id=uuid4(),
        clinica_id=clinica_id,
        criado_em=agora,
        atualizado_em=agora,
        deletado=False,
        deletado_em=None,
        paciente_id=paciente_id,
        data=date(2026, 1, 5),
        titulo=titulo,
        prioridade=PrioridadeTarefa.ALTA,
        concluido=concluido,
        concluido_em=agora if concluido else None,
    )


async def test_duplicar_cria_copias_nao_concluidas_em_nova_data():
    clinica_id = uuid4()
    paciente_id = uuid4()
    repository = FakeTarefaRepository()

    t1 = await repository.salvar(_tarefa(clinica_id, paciente_id, "Tarefa 1", concluido=True))
    t2 = await repository.salvar(_tarefa(clinica_id, paciente_id, "Tarefa 2"))
    await repository.salvar(_tarefa(clinica_id, paciente_id, "Tarefa 3 - nao selecionada"))

    nova_data = date(2026, 1, 12)
    copias = await DuplicarTarefasUseCase(repository).executar(
        paciente_id,
        DuplicarTarefasInputDTO(tarefa_ids=[t1.id, t2.id], nova_data=nova_data),
        clinica_id,
        PapelUsuario.FONO,
    )

    assert len(copias) == 2
    assert {c.titulo for c in copias} == {"Tarefa 1", "Tarefa 2"}
    assert all(c.concluido is False for c in copias)
    assert all(c.concluido_em is None for c in copias)
    assert all(c.data == nova_data for c in copias)
    assert all(c.id not in {t1.id, t2.id} for c in copias)

    # originais intactos
    original = await repository.buscar_por_id(t1.id, clinica_id)
    assert original is not None
    assert original.concluido is True
