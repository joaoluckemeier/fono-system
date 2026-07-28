"""Seed manual de desenvolvimento: uma clinica + um usuario admin para teste de login.

Uso: uv run python scripts/seed_dev.py
"""

import asyncio
from datetime import UTC, datetime
from uuid import uuid4

from backend.domain.entities.clinica import Clinica, PlanoClinica
from backend.domain.entities.usuario import PapelUsuario, Usuario
from backend.infrastructure.auth.password_hasher import hash_senha
from backend.infrastructure.database.connection import async_session_factory
from backend.infrastructure.repositories.clinica_repository import ClinicaRepositoryImpl
from backend.infrastructure.repositories.usuario_repository import UsuarioRepositoryImpl

EMAIL_SEED = "beta@clinica.com"
SENHA_SEED = "senha_teste"


async def main() -> None:
    async with async_session_factory() as session:
        clinica_repo = ClinicaRepositoryImpl(session)
        usuario_repo = UsuarioRepositoryImpl(session)

        usuario_existente = await usuario_repo.buscar_por_email(EMAIL_SEED)
        if usuario_existente is not None:
            print(f"Usuario de seed ja existe: {EMAIL_SEED}")
            return

        clinica = await clinica_repo.salvar(
            Clinica(id=uuid4(), nome="Clinica Beta", plano=PlanoClinica.BASICO, criado_em=datetime.now(UTC))
        )

        agora = datetime.now(UTC)
        await usuario_repo.salvar(
            Usuario(
                id=uuid4(),
                clinica_id=clinica.id,
                criado_em=agora,
                atualizado_em=agora,
                deletado=False,
                deletado_em=None,
                email=EMAIL_SEED,
                senha_hash=hash_senha(SENHA_SEED),
                nome="Beta Fonoaudiologa",
                papel=PapelUsuario.ADMIN,
                ativo=True,
                ultimo_login_em=None,
            )
        )

        print(f"Seed criado: clinica={clinica.id} usuario={EMAIL_SEED} senha={SENHA_SEED}")


if __name__ == "__main__":
    asyncio.run(main())
