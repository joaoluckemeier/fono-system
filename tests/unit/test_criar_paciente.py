from datetime import date
from uuid import uuid4

import pytest

from backend.application.dtos.paciente_dto import CriarPacienteInputDTO
from backend.application.use_cases.pacientes.criar_paciente import CriarPacienteUseCase
from backend.domain.entities.usuario import PapelUsuario
from tests.unit.fakes import FakePacienteRepository


def _dto() -> CriarPacienteInputDTO:
    return CriarPacienteInputDTO(
        nome_completo="Joao Silva",
        data_nascimento=date(2018, 5, 10),
        nome_mae="Maria Silva",
        nome_pai="Pedro Silva",
        tem_irmaos=False,
        faz_uso_medicamento="nao",
        diagnostico="TEA leve",
        informacoes_nascimento="Parto normal, sem intercorrencias",
        queixa_principal="Atraso de fala",
        observacoes="Familia colaborativa",
    )


@pytest.mark.parametrize("papel", [PapelUsuario.ADMIN, PapelUsuario.FONO, PapelUsuario.SECRETARIA])
async def test_criar_paciente_valido_qualquer_papel(papel):
    use_case = CriarPacienteUseCase(FakePacienteRepository())
    clinica_id = uuid4()

    paciente = await use_case.executar(_dto(), clinica_id, papel)

    assert paciente.nome_completo == "Joao Silva"
    assert paciente.clinica_id == clinica_id
    assert paciente.diagnostico == "TEA leve"
    assert paciente.informacoes_nascimento == "Parto normal, sem intercorrencias"
    assert paciente.queixa_principal == "Atraso de fala"
    assert paciente.observacoes == "Familia colaborativa"


async def test_idade_calculada_a_partir_da_data_nascimento():
    hoje = date.today()
    data_nascimento = date(hoje.year - 8, hoje.month, hoje.day)
    idade_esperada = 8

    dto = CriarPacienteInputDTO(
        nome_completo="Joao Silva",
        data_nascimento=data_nascimento,
        nome_mae="Maria Silva",
        nome_pai="Pedro Silva",
        tem_irmaos=False,
        faz_uso_medicamento="nao",
    )
    use_case = CriarPacienteUseCase(FakePacienteRepository())

    paciente = await use_case.executar(dto, uuid4(), PapelUsuario.ADMIN)

    assert paciente.idade == idade_esperada


async def test_criar_paciente_persiste_no_repositorio():
    repository = FakePacienteRepository()
    use_case = CriarPacienteUseCase(repository)
    clinica_id = uuid4()

    paciente = await use_case.executar(_dto(), clinica_id, PapelUsuario.ADMIN)

    salvo = await repository.buscar_por_id(paciente.id, clinica_id)
    assert salvo is not None
    assert salvo.nome_completo == "Joao Silva"
