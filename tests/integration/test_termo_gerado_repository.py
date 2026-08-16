from datetime import UTC, date, datetime
from uuid import uuid4

from backend.domain.entities.anexo import Anexo, EntidadeAnexavel, TipoArquivo
from backend.domain.entities.clinica import Clinica, PlanoClinica
from backend.domain.entities.modelo_termo import ModeloTermo, TipoModeloTermo
from backend.domain.entities.paciente import Paciente
from backend.domain.entities.termo_gerado import TermoGerado
from backend.domain.entities.usuario import PapelUsuario, Usuario
from backend.infrastructure.auth.password_hasher import hash_senha
from backend.infrastructure.repositories.anexo_repository import AnexoRepositoryImpl
from backend.infrastructure.repositories.clinica_repository import ClinicaRepositoryImpl
from backend.infrastructure.repositories.modelo_termo_repository import ModeloTermoRepositoryImpl
from backend.infrastructure.repositories.paciente_repository import PacienteRepositoryImpl
from backend.infrastructure.repositories.termo_gerado_repository import TermoGeradoRepositoryImpl
from backend.infrastructure.repositories.usuario_repository import UsuarioRepositoryImpl


async def _preparar_dependencias(db_session):
    agora = datetime.now(UTC)

    clinica = await ClinicaRepositoryImpl(db_session).salvar(
        Clinica(id=uuid4(), nome="Clinica de Teste", plano=PlanoClinica.BASICO, criado_em=agora)
    )

    paciente = await PacienteRepositoryImpl(db_session).salvar(
        Paciente(
            id=uuid4(),
            clinica_id=clinica.id,
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
        )
    )

    usuario = await UsuarioRepositoryImpl(db_session).salvar(
        Usuario(
            id=uuid4(),
            clinica_id=clinica.id,
            criado_em=agora,
            atualizado_em=agora,
            deletado=False,
            deletado_em=None,
            email=f"fono-{uuid4()}@clinica.com",
            senha_hash=hash_senha("senha_teste"),
            nome="Fono Teste",
            papel=PapelUsuario.FONO,
            ativo=True,
            ultimo_login_em=None,
        )
    )

    modelo = await ModeloTermoRepositoryImpl(db_session).salvar(
        ModeloTermo(
            id=uuid4(),
            clinica_id=clinica.id,
            criado_em=agora,
            atualizado_em=agora,
            deletado=False,
            deletado_em=None,
            nome="Termo de avaliacao",
            tipo=TipoModeloTermo.TERMO,
            corpo_texto="texto do termo",
        )
    )

    anexo = await AnexoRepositoryImpl(db_session).salvar(
        Anexo(
            id=uuid4(),
            clinica_id=clinica.id,
            criado_em=agora,
            atualizado_em=agora,
            deletado=False,
            deletado_em=None,
            entidade_tipo=EntidadeAnexavel.PACIENTE,
            entidade_id=paciente.id,
            tipo_arquivo=TipoArquivo.PDF,
            nome_arquivo="termo.pdf",
            storage_ref="minio://bucket/termo.pdf",
            criado_por=usuario.id,
        )
    )

    return clinica.id, paciente.id, modelo.id, anexo.id, usuario.id


def _novo_termo_gerado(clinica_id, paciente_id, modelo_id, anexo_id, usuario_id) -> TermoGerado:
    agora = datetime.now(UTC)
    return TermoGerado(
        id=uuid4(),
        clinica_id=clinica_id,
        criado_em=agora,
        atualizado_em=agora,
        deletado=False,
        deletado_em=None,
        paciente_id=paciente_id,
        modelo_id=modelo_id,
        anexo_id=anexo_id,
        gerado_por=usuario_id,
    )


async def test_criar_e_listar_por_paciente(db_session):
    clinica_id, paciente_id, modelo_id, anexo_id, usuario_id = await _preparar_dependencias(
        db_session
    )
    repository = TermoGeradoRepositoryImpl(db_session)

    salvo = await repository.salvar(
        _novo_termo_gerado(clinica_id, paciente_id, modelo_id, anexo_id, usuario_id)
    )

    historico = await repository.listar_por_paciente(paciente_id, clinica_id)
    assert [t.id for t in historico] == [salvo.id]
    assert historico[0].anexo_id == anexo_id


async def test_soft_delete_remove_da_listagem(db_session):
    clinica_id, paciente_id, modelo_id, anexo_id, usuario_id = await _preparar_dependencias(
        db_session
    )
    repository = TermoGeradoRepositoryImpl(db_session)
    termo = await repository.salvar(
        _novo_termo_gerado(clinica_id, paciente_id, modelo_id, anexo_id, usuario_id)
    )

    await repository.soft_delete(termo.id, clinica_id)

    assert await repository.buscar_por_id(termo.id, clinica_id) is None
    assert await repository.listar_por_paciente(paciente_id, clinica_id) == []


async def test_filtro_por_clinica_isola_termos(db_session):
    clinica_id, paciente_id, modelo_id, anexo_id, usuario_id = await _preparar_dependencias(
        db_session
    )
    repository = TermoGeradoRepositoryImpl(db_session)
    await repository.salvar(
        _novo_termo_gerado(clinica_id, paciente_id, modelo_id, anexo_id, usuario_id)
    )

    outra_clinica_id, outro_paciente_id, outro_modelo_id, outro_anexo_id, outro_usuario_id = (
        await _preparar_dependencias(db_session)
    )
    await repository.salvar(
        _novo_termo_gerado(
            outra_clinica_id, outro_paciente_id, outro_modelo_id, outro_anexo_id, outro_usuario_id
        )
    )

    assert await repository.listar_por_paciente(paciente_id, outra_clinica_id) == []
