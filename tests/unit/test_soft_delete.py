from datetime import date
from uuid import uuid4

from backend.application.dtos.paciente_dto import CriarPacienteInputDTO
from backend.application.use_cases.pacientes.criar_paciente import CriarPacienteUseCase
from backend.application.use_cases.pacientes.deletar_paciente import DeletarPacienteUseCase
from backend.application.use_cases.pacientes.listar_pacientes import ListarPacientesUseCase
from backend.domain.entities.usuario import PapelUsuario
from tests.unit.fakes import FakePacienteRepository


async def test_registro_deletado_nao_aparece_em_listagens():
    repository = FakePacienteRepository()
    clinica_id = uuid4()

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

    antes = await ListarPacientesUseCase(repository).executar(clinica_id)
    assert len(antes) == 1

    await DeletarPacienteUseCase(repository).executar(paciente.id, clinica_id, PapelUsuario.ADMIN)

    depois = await ListarPacientesUseCase(repository).executar(clinica_id)
    assert depois == []

    # o registro continua no banco (soft delete), so nao aparece em listagens/busca
    direto = await repository.buscar_por_id(paciente.id, clinica_id)
    assert direto is None
    assert repository._pacientes[paciente.id].deletado is True
