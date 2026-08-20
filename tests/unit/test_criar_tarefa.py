from datetime import date
from uuid import uuid4

import pytest

from backend.application.dtos.paciente_dto import CriarPacienteInputDTO
from backend.application.dtos.tarefa_dto import CriarTarefaInputDTO
from backend.application.exceptions import RecursoNaoEncontradoError
from backend.application.use_cases.pacientes.criar_paciente import CriarPacienteUseCase
from backend.application.use_cases.tarefas.criar_tarefa import CriarTarefaUseCase
from backend.domain.entities.usuario import PapelUsuario
from tests.unit.fakes import FakePacienteRepository, FakeTarefaRepository


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


async def test_criar_tarefa_com_prioridade_padrao():
    clinica_id = uuid4()
    paciente_repository = FakePacienteRepository()
    paciente = await _paciente_para_teste(paciente_repository, clinica_id)

    use_case = CriarTarefaUseCase(FakeTarefaRepository(), paciente_repository)
    tarefa = await use_case.executar(
        paciente.id,
        CriarTarefaInputDTO(data=date(2026, 1, 5), titulo="Exercicio de sopro"),
        clinica_id,
        PapelUsuario.FONO,
    )

    assert tarefa.titulo == "Exercicio de sopro"
    assert tarefa.prioridade == "media"
    assert tarefa.concluido is False


async def test_criar_tarefa_paciente_inexistente():
    use_case = CriarTarefaUseCase(FakeTarefaRepository(), FakePacienteRepository())

    with pytest.raises(RecursoNaoEncontradoError):
        await use_case.executar(
            uuid4(),
            CriarTarefaInputDTO(data=date(2026, 1, 5), titulo="Exercicio"),
            uuid4(),
            PapelUsuario.FONO,
        )
