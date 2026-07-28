from datetime import UTC, date, datetime
from uuid import uuid4

from backend.domain.entities.clinica import Clinica, PlanoClinica
from backend.domain.entities.paciente import Paciente
from backend.infrastructure.repositories.clinica_repository import ClinicaRepositoryImpl
from backend.infrastructure.repositories.paciente_repository import PacienteRepositoryImpl


async def _nova_clinica(db_session) -> object:
    clinica = Clinica(
        id=uuid4(), nome="Clinica de Teste", plano=PlanoClinica.BASICO, criado_em=datetime.now(UTC)
    )
    salva = await ClinicaRepositoryImpl(db_session).salvar(clinica)
    return salva.id


def _novo_paciente(clinica_id) -> Paciente:
    agora = datetime.now(UTC)
    return Paciente(
        id=uuid4(),
        clinica_id=clinica_id,
        criado_em=agora,
        atualizado_em=agora,
        deletado=False,
        deletado_em=None,
        nome_completo="Joao Silva",
        data_nascimento=date(2018, 5, 10),
        nome_mae="Maria Silva",
        nome_pai="Pedro Silva",
        tem_irmaos=False,
        faz_uso_medicamento="nao",
        diagnostico="TEA leve",
    )


async def test_criar_e_buscar_paciente(db_session):
    repository = PacienteRepositoryImpl(db_session)
    clinica_id = await _nova_clinica(db_session)
    paciente = _novo_paciente(clinica_id)

    await repository.salvar(paciente)
    encontrado = await repository.buscar_por_id(paciente.id, clinica_id)

    assert encontrado is not None
    assert encontrado.nome_completo == "Joao Silva"
    assert encontrado.diagnostico == "TEA leve"


async def test_atualizar_paciente(db_session):
    repository = PacienteRepositoryImpl(db_session)
    clinica_id = await _nova_clinica(db_session)
    paciente = await repository.salvar(_novo_paciente(clinica_id))

    paciente.nome_completo = "Joao Silva Atualizado"
    await repository.salvar(paciente)

    encontrado = await repository.buscar_por_id(paciente.id, clinica_id)
    assert encontrado.nome_completo == "Joao Silva Atualizado"


async def test_soft_delete_remove_da_listagem_mas_mantem_no_banco(db_session):
    repository = PacienteRepositoryImpl(db_session)
    clinica_id = await _nova_clinica(db_session)
    paciente = await repository.salvar(_novo_paciente(clinica_id))

    await repository.soft_delete(paciente.id, clinica_id)

    assert await repository.buscar_por_id(paciente.id, clinica_id) is None
    assert paciente.id not in [p.id for p in await repository.listar(clinica_id)]


async def test_filtro_por_clinica_isola_pacientes(db_session):
    repository = PacienteRepositoryImpl(db_session)
    clinica_a = await _nova_clinica(db_session)
    clinica_b = await _nova_clinica(db_session)

    paciente_a = await repository.salvar(_novo_paciente(clinica_a))
    await repository.salvar(_novo_paciente(clinica_b))

    listagem_a = await repository.listar(clinica_a)
    assert [p.id for p in listagem_a] == [paciente_a.id]

    # buscar paciente da clinica A usando clinica_id errado nao deve retornar nada
    assert await repository.buscar_por_id(paciente_a.id, clinica_b) is None
