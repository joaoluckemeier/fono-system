from datetime import date
from uuid import uuid4

import pytest

from backend.application.dtos.evolucao_dto import CriarEvolucaoInputDTO
from backend.application.dtos.paciente_dto import CriarPacienteInputDTO
from backend.application.dtos.tarefa_dto import CriarTarefaInputDTO
from backend.application.exceptions import PermissaoNegadaError
from backend.application.use_cases.evolucoes.criar_evolucao import CriarEvolucaoUseCase
from backend.application.use_cases.evolucoes.listar_evolucoes import ListarEvolucoesUseCase
from backend.application.use_cases.pacientes.criar_paciente import CriarPacienteUseCase
from backend.application.use_cases.tarefas.criar_tarefa import CriarTarefaUseCase
from backend.application.use_cases.tarefas.listar_tarefas_paciente import (
    ListarTarefasPacienteUseCase,
)
from backend.domain.authorization.policy import Recurso, usuario_pode
from backend.domain.entities.usuario import PapelUsuario
from tests.unit.fakes import FakeEvolucaoRepository, FakePacienteRepository, FakeTarefaRepository


def test_secretaria_nao_ve_diagnostico_na_politica():
    assert usuario_pode(PapelUsuario.SECRETARIA, Recurso.PACIENTE_CLINICO) is False
    assert usuario_pode(PapelUsuario.ADMIN, Recurso.PACIENTE_CLINICO) is True
    assert usuario_pode(PapelUsuario.FONO, Recurso.PACIENTE_CLINICO) is True


def test_secretaria_nao_acessa_evolucao_na_politica():
    assert usuario_pode(PapelUsuario.SECRETARIA, Recurso.EVOLUCAO) is False
    assert usuario_pode(PapelUsuario.ADMIN, Recurso.EVOLUCAO) is True
    assert usuario_pode(PapelUsuario.FONO, Recurso.EVOLUCAO) is True


def test_apenas_admin_gerencia_modelos_de_termo():
    assert usuario_pode(PapelUsuario.ADMIN, Recurso.TERMO_MODELO) is True
    assert usuario_pode(PapelUsuario.FONO, Recurso.TERMO_MODELO) is False
    assert usuario_pode(PapelUsuario.SECRETARIA, Recurso.TERMO_MODELO) is False


def test_admin_e_fono_geram_termo():
    assert usuario_pode(PapelUsuario.ADMIN, Recurso.TERMO_GERACAO) is True
    assert usuario_pode(PapelUsuario.FONO, Recurso.TERMO_GERACAO) is True
    assert usuario_pode(PapelUsuario.SECRETARIA, Recurso.TERMO_GERACAO) is False


def test_secretaria_nao_acessa_planejamento_na_politica():
    assert usuario_pode(PapelUsuario.SECRETARIA, Recurso.PLANEJAMENTO_TERAPEUTICO) is False
    assert usuario_pode(PapelUsuario.ADMIN, Recurso.PLANEJAMENTO_TERAPEUTICO) is True
    assert usuario_pode(PapelUsuario.FONO, Recurso.PLANEJAMENTO_TERAPEUTICO) is True


async def _paciente_para_teste(paciente_repository: FakePacienteRepository, clinica_id):
    return await CriarPacienteUseCase(paciente_repository).executar(
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


async def test_secretaria_nao_cria_evolucao():
    clinica_id = uuid4()
    paciente_repository = FakePacienteRepository()
    paciente = await _paciente_para_teste(paciente_repository, clinica_id)

    use_case = CriarEvolucaoUseCase(FakeEvolucaoRepository(), paciente_repository)

    with pytest.raises(PermissaoNegadaError):
        await use_case.executar(
            paciente.id,
            CriarEvolucaoInputDTO(data=date(2026, 1, 1), texto="tentativa"),
            clinica_id,
            uuid4(),
            PapelUsuario.SECRETARIA,
        )


async def test_secretaria_nao_lista_evolucoes():
    with pytest.raises(PermissaoNegadaError):
        await ListarEvolucoesUseCase(FakeEvolucaoRepository()).executar(
            uuid4(), uuid4(), PapelUsuario.SECRETARIA
        )


async def test_fono_cria_evolucao_com_sucesso():
    clinica_id = uuid4()
    paciente_repository = FakePacienteRepository()
    paciente = await _paciente_para_teste(paciente_repository, clinica_id)

    use_case = CriarEvolucaoUseCase(FakeEvolucaoRepository(), paciente_repository)

    evolucao = await use_case.executar(
        paciente.id,
        CriarEvolucaoInputDTO(data=date(2026, 1, 1), texto="evolucao valida"),
        clinica_id,
        uuid4(),
        PapelUsuario.FONO,
    )

    assert evolucao.texto == "evolucao valida"


async def test_secretaria_nao_cria_tarefa():
    clinica_id = uuid4()
    paciente_repository = FakePacienteRepository()
    paciente = await _paciente_para_teste(paciente_repository, clinica_id)

    use_case = CriarTarefaUseCase(FakeTarefaRepository(), paciente_repository)

    with pytest.raises(PermissaoNegadaError):
        await use_case.executar(
            paciente.id,
            CriarTarefaInputDTO(data=date(2026, 1, 1), titulo="tentativa"),
            clinica_id,
            PapelUsuario.SECRETARIA,
        )


async def test_secretaria_nao_lista_tarefas():
    with pytest.raises(PermissaoNegadaError):
        await ListarTarefasPacienteUseCase(FakeTarefaRepository()).executar(
            uuid4(), uuid4(), PapelUsuario.SECRETARIA
        )
