from datetime import UTC, datetime
from uuid import uuid4

import pytest

from backend.application.exceptions import PermissaoNegadaError, RecursoNaoEncontradoError
from backend.application.use_cases.anexos.buscar_url_anexo import BuscarUrlAnexoUseCase
from backend.domain.entities.anexo import Anexo, EntidadeAnexavel, TipoArquivo
from backend.domain.entities.usuario import PapelUsuario
from tests.unit.fakes import FakeAnexoRepository, FakeStorageService


def _anexo(clinica_id, entidade_tipo=EntidadeAnexavel.PACIENTE) -> Anexo:
    agora = datetime.now(UTC)
    return Anexo(
        id=uuid4(),
        clinica_id=clinica_id,
        criado_em=agora,
        atualizado_em=agora,
        deletado=False,
        deletado_em=None,
        entidade_tipo=entidade_tipo,
        entidade_id=uuid4(),
        tipo_arquivo=TipoArquivo.FOTO,
        nome_arquivo="foto.jpg",
        storage_ref="minio://bucket/foto.jpg",
        criado_por=uuid4(),
    )


async def test_busca_url_com_sucesso():
    clinica_id = uuid4()
    anexo = _anexo(clinica_id)
    repository = FakeAnexoRepository([anexo])
    storage = FakeStorageService()
    use_case = BuscarUrlAnexoUseCase(repository, storage)

    url = await use_case.executar(anexo.id, clinica_id, PapelUsuario.ADMIN)

    assert url == anexo.storage_ref


async def test_secretaria_nao_ve_url_de_anexo_clinico():
    clinica_id = uuid4()
    anexo = _anexo(clinica_id, entidade_tipo=EntidadeAnexavel.EVOLUCAO)
    repository = FakeAnexoRepository([anexo])
    use_case = BuscarUrlAnexoUseCase(repository, FakeStorageService())

    with pytest.raises(PermissaoNegadaError):
        await use_case.executar(anexo.id, clinica_id, PapelUsuario.SECRETARIA)


async def test_clinica_id_errado_nao_encontra_anexo():
    clinica_id = uuid4()
    anexo = _anexo(clinica_id)
    repository = FakeAnexoRepository([anexo])
    use_case = BuscarUrlAnexoUseCase(repository, FakeStorageService())

    with pytest.raises(RecursoNaoEncontradoError):
        await use_case.executar(anexo.id, uuid4(), PapelUsuario.ADMIN)
