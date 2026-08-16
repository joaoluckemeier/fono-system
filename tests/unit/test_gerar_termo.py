from datetime import UTC, date, datetime
from uuid import uuid4

import pytest

from backend.application.dtos.paciente_dto import CriarPacienteInputDTO
from backend.application.dtos.termo_gerado_dto import GerarTermoInputDTO
from backend.application.exceptions import PermissaoNegadaError, RecursoNaoEncontradoError
from backend.application.use_cases.pacientes.criar_paciente import CriarPacienteUseCase
from backend.application.use_cases.termos.gerar_termo import GerarTermoUseCase, _mesclar_placeholders
from backend.domain.entities.clinica import Clinica, PlanoClinica
from backend.domain.entities.modelo_termo import ModeloTermo, TipoModeloTermo
from backend.domain.entities.usuario import PapelUsuario
from tests.unit.fakes import (
    FakeAnexoRepository,
    FakeClinicaRepository,
    FakeGeradorDocumento,
    FakeModeloTermoRepository,
    FakePacienteRepository,
    FakeStorageService,
    FakeTermoGeradoRepository,
)


def test_mesclar_placeholders_isolado():
    corpo = "Paciente {{nome_paciente}}, idade {{idade}}."
    resultado = _mesclar_placeholders(corpo, {"nome_paciente": "Joao Silva", "idade": "8"})
    assert resultado == "Paciente Joao Silva, idade 8."


def _modelo(clinica_id, ativo=True) -> ModeloTermo:
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
    ) if ativo else ModeloTermo(
        id=uuid4(),
        clinica_id=clinica_id,
        criado_em=agora,
        atualizado_em=agora,
        deletado=False,
        deletado_em=None,
        nome="Termo desativado",
        tipo=TipoModeloTermo.TERMO,
        corpo_texto="texto",
        ativo=False,
    )


async def _monta_caso(clinica_id, modelo_ativo=True):
    paciente_repository = FakePacienteRepository()
    paciente = await CriarPacienteUseCase(paciente_repository).executar(
        CriarPacienteInputDTO(
            nome_completo="Joao Silva",
            data_nascimento=date(2018, 5, 10),
            nome_mae="Maria Silva",
            nome_pai="Pedro Silva",
            tem_irmaos=False,
            faz_uso_medicamento="nao",
        ),
        clinica_id,
        PapelUsuario.ADMIN,
    )
    modelo_repository = FakeModeloTermoRepository([_modelo(clinica_id, ativo=modelo_ativo)])
    modelo = (await modelo_repository.listar(clinica_id))[0]
    clinica_repository = FakeClinicaRepository(
        [Clinica(id=clinica_id, nome="Clinica de Teste", plano=PlanoClinica.BASICO, criado_em=datetime.now(UTC))]
    )
    termo_gerado_repository = FakeTermoGeradoRepository()
    anexo_repository = FakeAnexoRepository()
    storage = FakeStorageService()
    gerador = FakeGeradorDocumento()

    use_case = GerarTermoUseCase(
        modelo_repository,
        paciente_repository,
        clinica_repository,
        termo_gerado_repository,
        anexo_repository,
        storage,
        gerador,
    )
    return use_case, paciente, modelo, anexo_repository, termo_gerado_repository, gerador


async def test_gerar_termo_caminho_feliz():
    clinica_id = uuid4()
    use_case, paciente, modelo, anexo_repository, termo_gerado_repository, gerador = (
        await _monta_caso(clinica_id)
    )

    resultado = await use_case.executar(
        paciente.id,
        GerarTermoInputDTO(modelo_id=modelo.id),
        clinica_id,
        uuid4(),
        "Dra. Ana",
        PapelUsuario.FONO,
    )

    assert resultado.pdf_bytes == b"%PDF-FAKE"
    assert "Joao Silva" in gerador.chamadas[0][1]

    anexos = await anexo_repository.listar(clinica_id)
    assert len(anexos) == 1
    assert anexos[0].id == resultado.termo.anexo_id

    termos = await termo_gerado_repository.listar_por_paciente(paciente.id, clinica_id)
    assert len(termos) == 1
    assert termos[0].modelo_id == modelo.id


async def test_modelo_inativo_gera_erro():
    clinica_id = uuid4()
    use_case, paciente, modelo, *_ = await _monta_caso(clinica_id, modelo_ativo=False)

    with pytest.raises(ValueError):
        await use_case.executar(
            paciente.id,
            GerarTermoInputDTO(modelo_id=modelo.id),
            clinica_id,
            uuid4(),
            "Dra. Ana",
            PapelUsuario.FONO,
        )


async def test_secretaria_nao_gera_termo():
    clinica_id = uuid4()
    use_case, paciente, modelo, *_ = await _monta_caso(clinica_id)

    with pytest.raises(PermissaoNegadaError):
        await use_case.executar(
            paciente.id,
            GerarTermoInputDTO(modelo_id=modelo.id),
            clinica_id,
            uuid4(),
            "Secretaria",
            PapelUsuario.SECRETARIA,
        )


async def test_paciente_inexistente_gera_erro():
    clinica_id = uuid4()
    use_case, _paciente, modelo, *_ = await _monta_caso(clinica_id)

    with pytest.raises(RecursoNaoEncontradoError):
        await use_case.executar(
            uuid4(),
            GerarTermoInputDTO(modelo_id=modelo.id),
            clinica_id,
            uuid4(),
            "Dra. Ana",
            PapelUsuario.FONO,
        )
