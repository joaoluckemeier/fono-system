from datetime import UTC, date, datetime
from uuid import uuid4

from backend.application.dtos.evolucao_dto import ConfirmarEvolucaoInputDTO
from backend.application.use_cases.evolucoes.confirmar_evolucao import ConfirmarEvolucaoUseCase
from backend.domain.entities.evolucao import Evolucao, StatusEvolucao
from backend.domain.entities.usuario import PapelUsuario
from tests.unit.fakes import FakeEvolucaoRepository, FakeStorageService


async def _evolucao_pendente(evolucao_repository: FakeEvolucaoRepository, audio_ref: str | None):
    agora = datetime.now(UTC)
    evolucao = Evolucao(
        id=uuid4(),
        clinica_id=uuid4(),
        criado_em=agora,
        atualizado_em=agora,
        deletado=False,
        deletado_em=None,
        paciente_id=uuid4(),
        usuario_id=uuid4(),
        data=date.today(),
        texto="rascunho gerado por IA",
        status=StatusEvolucao.PENDENTE_REVISAO,
        audio_ref=audio_ref,
    )
    return await evolucao_repository.salvar(evolucao)


async def test_confirmar_evolucao_muda_status_e_apaga_audio():
    evolucao_repository = FakeEvolucaoRepository()
    storage = FakeStorageService()
    audio_ref = await storage.salvar(b"audio", "sessao.webm")
    pendente = await _evolucao_pendente(evolucao_repository, audio_ref)

    use_case = ConfirmarEvolucaoUseCase(evolucao_repository, storage)
    confirmada = await use_case.executar(
        pendente.id, ConfirmarEvolucaoInputDTO(), pendente.clinica_id, PapelUsuario.FONO
    )

    assert confirmada.status == StatusEvolucao.CONFIRMADA.value
    assert audio_ref in storage.deletados


async def test_confirmar_evolucao_permite_editar_texto_final():
    evolucao_repository = FakeEvolucaoRepository()
    storage = FakeStorageService()
    pendente = await _evolucao_pendente(evolucao_repository, None)

    use_case = ConfirmarEvolucaoUseCase(evolucao_repository, storage)
    confirmada = await use_case.executar(
        pendente.id,
        ConfirmarEvolucaoInputDTO(texto_final="texto revisado pela fono"),
        pendente.clinica_id,
        PapelUsuario.FONO,
    )

    assert confirmada.texto == "texto revisado pela fono"
    assert confirmada.status == StatusEvolucao.CONFIRMADA.value
