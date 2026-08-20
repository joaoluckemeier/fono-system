from datetime import UTC, date, datetime
from uuid import uuid4

from backend.domain.entities.clinica import Clinica, PlanoClinica
from backend.domain.entities.paciente import Paciente
from backend.domain.entities.tarefa import Tarefa
from backend.infrastructure.repositories.clinica_repository import ClinicaRepositoryImpl
from backend.infrastructure.repositories.paciente_repository import PacienteRepositoryImpl
from backend.infrastructure.repositories.tarefa_repository import TarefaRepositoryImpl


async def _criar_clinica(db_session):
    agora = datetime.now(UTC)
    clinica = await ClinicaRepositoryImpl(db_session).salvar(
        Clinica(id=uuid4(), nome="Clinica de Teste", plano=PlanoClinica.BASICO, criado_em=agora)
    )
    return clinica.id


async def _criar_paciente(db_session, clinica_id, nome_paciente: str = "Joao Silva"):
    agora = datetime.now(UTC)
    paciente = await PacienteRepositoryImpl(db_session).salvar(
        Paciente(
            id=uuid4(),
            clinica_id=clinica_id,
            criado_em=agora,
            atualizado_em=agora,
            deletado=False,
            deletado_em=None,
            nome_completo=nome_paciente,
            data_nascimento=date(2018, 5, 10),
            nome_mae="Maria Silva",
            nome_pai="Pedro Silva",
            tem_irmaos=False,
            faz_uso_medicamento="nao",
        )
    )
    return paciente.id


async def _preparar_clinica_e_paciente(db_session, nome_paciente: str = "Joao Silva"):
    clinica_id = await _criar_clinica(db_session)
    paciente_id = await _criar_paciente(db_session, clinica_id, nome_paciente)
    return clinica_id, paciente_id


def _nova_tarefa(clinica_id, paciente_id, data: date, titulo: str) -> Tarefa:
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


async def test_listar_por_paciente_periodo_filtra_por_data(db_session):
    clinica_id, paciente_id = await _preparar_clinica_e_paciente(db_session)
    repository = TarefaRepositoryImpl(db_session)

    await repository.salvar(_nova_tarefa(clinica_id, paciente_id, date(2026, 1, 5), "dentro 1"))
    await repository.salvar(_nova_tarefa(clinica_id, paciente_id, date(2026, 1, 9), "dentro 2"))
    await repository.salvar(_nova_tarefa(clinica_id, paciente_id, date(2026, 2, 1), "fora"))

    resultado = await repository.listar_por_paciente_periodo(
        paciente_id, clinica_id, date(2026, 1, 5), date(2026, 1, 11)
    )

    assert [t.titulo for t in resultado] == ["dentro 1", "dentro 2"]


async def test_listar_por_periodo_agrupa_multiplos_pacientes(db_session):
    clinica_id = await _criar_clinica(db_session)
    paciente_a = await _criar_paciente(db_session, clinica_id, "Paciente A")
    paciente_b = await _criar_paciente(db_session, clinica_id, "Paciente B")

    repository = TarefaRepositoryImpl(db_session)
    await repository.salvar(_nova_tarefa(clinica_id, paciente_a, date(2026, 1, 6), "A1"))
    await repository.salvar(_nova_tarefa(clinica_id, paciente_b, date(2026, 1, 7), "B1"))
    await repository.salvar(_nova_tarefa(clinica_id, paciente_a, date(2026, 3, 1), "fora do periodo"))

    resultado = await repository.listar_por_periodo(clinica_id, date(2026, 1, 5), date(2026, 1, 11))

    assert {t.titulo for t in resultado} == {"A1", "B1"}


async def test_soft_delete_nao_aparece_em_listagens(db_session):
    clinica_id, paciente_id = await _preparar_clinica_e_paciente(db_session)
    repository = TarefaRepositoryImpl(db_session)

    tarefa = await repository.salvar(
        _nova_tarefa(clinica_id, paciente_id, date(2026, 1, 5), "a ser removida")
    )
    await repository.soft_delete(tarefa.id, clinica_id)

    assert await repository.buscar_por_id(tarefa.id, clinica_id) is None
    assert await repository.listar_por_paciente_periodo(
        paciente_id, clinica_id, date(2026, 1, 1), date(2026, 1, 31)
    ) == []
