from datetime import UTC, date, datetime
from uuid import uuid4

from backend.domain.entities.clinica import Clinica, PlanoClinica
from backend.domain.entities.evolucao import Evolucao
from backend.domain.entities.paciente import Paciente
from backend.domain.entities.usuario import PapelUsuario, Usuario
from backend.infrastructure.auth.password_hasher import hash_senha
from backend.infrastructure.repositories.clinica_repository import ClinicaRepositoryImpl
from backend.infrastructure.repositories.evolucao_repository import EvolucaoRepositoryImpl
from backend.infrastructure.repositories.paciente_repository import PacienteRepositoryImpl
from backend.infrastructure.repositories.usuario_repository import UsuarioRepositoryImpl


async def _preparar_paciente_e_usuario(db_session):
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

    return clinica.id, paciente.id, usuario.id


def _nova_evolucao(clinica_id, paciente_id, usuario_id, data: date, texto: str) -> Evolucao:
    agora = datetime.now(UTC)
    return Evolucao(
        id=uuid4(),
        clinica_id=clinica_id,
        criado_em=agora,
        atualizado_em=agora,
        deletado=False,
        deletado_em=None,
        paciente_id=paciente_id,
        usuario_id=usuario_id,
        data=data,
        texto=texto,
    )


async def test_listar_por_paciente_retorna_historico_ordenado(db_session):
    clinica_id, paciente_id, usuario_id = await _preparar_paciente_e_usuario(db_session)
    repository = EvolucaoRepositoryImpl(db_session)

    await repository.salvar(
        _nova_evolucao(clinica_id, paciente_id, usuario_id, date(2026, 1, 1), "primeira sessao")
    )
    await repository.salvar(
        _nova_evolucao(clinica_id, paciente_id, usuario_id, date(2026, 3, 1), "terceira sessao")
    )
    await repository.salvar(
        _nova_evolucao(clinica_id, paciente_id, usuario_id, date(2026, 2, 1), "segunda sessao")
    )

    historico = await repository.listar_por_paciente(paciente_id, clinica_id)

    assert [e.texto for e in historico] == ["terceira sessao", "segunda sessao", "primeira sessao"]


async def test_buscar_ultima_devolutiva_e_a_mais_recente(db_session):
    clinica_id, paciente_id, usuario_id = await _preparar_paciente_e_usuario(db_session)
    repository = EvolucaoRepositoryImpl(db_session)

    await repository.salvar(
        _nova_evolucao(clinica_id, paciente_id, usuario_id, date(2026, 1, 1), "primeira sessao")
    )
    mais_recente = await repository.salvar(
        _nova_evolucao(clinica_id, paciente_id, usuario_id, date(2026, 5, 1), "sessao mais recente")
    )

    ultima = await repository.buscar_ultima(paciente_id, clinica_id)

    assert ultima is not None
    assert ultima.id == mais_recente.id
    assert ultima.texto == "sessao mais recente"


async def test_buscar_ultima_devolutiva_sem_evolucoes_retorna_none(db_session):
    _, paciente_id, _ = await _preparar_paciente_e_usuario(db_session)
    repository = EvolucaoRepositoryImpl(db_session)

    assert await repository.buscar_ultima(paciente_id, uuid4()) is None
