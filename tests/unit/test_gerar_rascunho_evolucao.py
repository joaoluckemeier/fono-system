from datetime import date
from uuid import uuid4

import pytest

from backend.application.dtos.paciente_dto import CriarPacienteInputDTO
from backend.application.exceptions import PermissaoNegadaError
from backend.application.use_cases.evolucoes.gerar_rascunho_evolucao import (
    GerarRascunhoEvolucaoUseCase,
    _sanitizar_transcricao,
)
from backend.application.use_cases.pacientes.criar_paciente import CriarPacienteUseCase
from backend.domain.entities.evolucao import StatusEvolucao
from backend.domain.entities.usuario import PapelUsuario
from tests.unit.fakes import (
    FakeAIGateway,
    FakeEvolucaoRepository,
    FakePacienteRepository,
    FakeStorageService,
    FakeTranscricaoService,
)


async def _paciente_para_teste(clinica_id):
    repository = FakePacienteRepository()
    paciente = await CriarPacienteUseCase(repository).executar(
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
    return repository, paciente


def test_sanitizar_transcricao_remove_nome_completo_e_primeiro_nome():
    from backend.domain.entities.paciente import Paciente

    paciente = Paciente(
        id=uuid4(),
        clinica_id=uuid4(),
        criado_em=None,
        atualizado_em=None,
        deletado=False,
        deletado_em=None,
        nome_completo="Joao Silva",
        data_nascimento=date(2018, 5, 10),
        nome_mae="Maria",
        nome_pai="Pedro",
        tem_irmaos=False,
        faz_uso_medicamento="nao",
    )

    resultado = _sanitizar_transcricao("Joao Silva chegou bem hoje. joao brincou bastante.", paciente)

    assert "Joao" not in resultado
    assert "[paciente]" in resultado


async def test_gerar_rascunho_cria_evolucao_pendente_revisao():
    clinica_id = uuid4()
    paciente_repository, paciente = await _paciente_para_teste(clinica_id)
    evolucao_repository = FakeEvolucaoRepository()
    ai_gateway = FakeAIGateway(rascunho="Paciente respondeu bem aos estimulos.")

    use_case = GerarRascunhoEvolucaoUseCase(
        evolucao_repository,
        paciente_repository,
        FakeStorageService(),
        FakeTranscricaoService(texto="sessao transcorreu normalmente"),
        ai_gateway,
    )

    evolucao = await use_case.executar(
        paciente.id, b"audio-fake", "sessao.webm", clinica_id, uuid4(), PapelUsuario.FONO
    )

    assert evolucao.status == StatusEvolucao.PENDENTE_REVISAO.value
    assert evolucao.texto == "Paciente respondeu bem aos estimulos."
    assert ai_gateway.ultimo_contexto == "sessao transcorreu normalmente"


async def test_secretaria_nao_gera_rascunho_de_evolucao():
    clinica_id = uuid4()
    paciente_repository, paciente = await _paciente_para_teste(clinica_id)

    use_case = GerarRascunhoEvolucaoUseCase(
        FakeEvolucaoRepository(),
        paciente_repository,
        FakeStorageService(),
        FakeTranscricaoService(),
        FakeAIGateway(),
    )

    with pytest.raises(PermissaoNegadaError):
        await use_case.executar(
            paciente.id, b"audio-fake", "sessao.webm", clinica_id, uuid4(), PapelUsuario.SECRETARIA
        )
