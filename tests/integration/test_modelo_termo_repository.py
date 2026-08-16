from datetime import UTC, datetime
from uuid import uuid4

from backend.domain.entities.clinica import Clinica, PlanoClinica
from backend.domain.entities.modelo_termo import ModeloTermo, TipoModeloTermo
from backend.infrastructure.repositories.clinica_repository import ClinicaRepositoryImpl
from backend.infrastructure.repositories.modelo_termo_repository import ModeloTermoRepositoryImpl


async def _nova_clinica(db_session):
    clinica = Clinica(
        id=uuid4(), nome="Clinica de Teste", plano=PlanoClinica.BASICO, criado_em=datetime.now(UTC)
    )
    salva = await ClinicaRepositoryImpl(db_session).salvar(clinica)
    return salva.id


def _novo_modelo(clinica_id) -> ModeloTermo:
    agora = datetime.now(UTC)
    return ModeloTermo(
        id=uuid4(),
        clinica_id=clinica_id,
        criado_em=agora,
        atualizado_em=agora,
        deletado=False,
        deletado_em=None,
        nome="Termo de avaliacao",
        tipo=TipoModeloTermo.TERMO,
        corpo_texto="Eu, responsavel por {{nome_paciente}}, autorizo a avaliacao.",
    )


async def test_criar_e_buscar_modelo_termo(db_session):
    repository = ModeloTermoRepositoryImpl(db_session)
    clinica_id = await _nova_clinica(db_session)

    salvo = await repository.salvar(_novo_modelo(clinica_id))
    encontrado = await repository.buscar_por_id(salvo.id, clinica_id)

    assert encontrado is not None
    assert encontrado.nome == "Termo de avaliacao"
    assert encontrado.ativo is True


async def test_atualizar_modelo_termo_desativa(db_session):
    repository = ModeloTermoRepositoryImpl(db_session)
    clinica_id = await _nova_clinica(db_session)
    modelo = await repository.salvar(_novo_modelo(clinica_id))

    modelo.ativo = False
    await repository.salvar(modelo)

    encontrado = await repository.buscar_por_id(modelo.id, clinica_id)
    assert encontrado.ativo is False


async def test_soft_delete_remove_da_listagem(db_session):
    repository = ModeloTermoRepositoryImpl(db_session)
    clinica_id = await _nova_clinica(db_session)
    modelo = await repository.salvar(_novo_modelo(clinica_id))

    await repository.soft_delete(modelo.id, clinica_id)

    assert await repository.buscar_por_id(modelo.id, clinica_id) is None
    assert modelo.id not in [m.id for m in await repository.listar(clinica_id)]


async def test_filtro_por_clinica_isola_modelos(db_session):
    repository = ModeloTermoRepositoryImpl(db_session)
    clinica_a = await _nova_clinica(db_session)
    clinica_b = await _nova_clinica(db_session)

    modelo_a = await repository.salvar(_novo_modelo(clinica_a))
    await repository.salvar(_novo_modelo(clinica_b))

    listagem_a = await repository.listar(clinica_a)
    assert [m.id for m in listagem_a] == [modelo_a.id]
