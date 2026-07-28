from collections.abc import AsyncIterator

import asyncpg
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from backend.config import get_settings
from backend.infrastructure.database.models import Base

_TEST_DB_NAME = "fono_test"


def _admin_url_and_test_url() -> tuple[str, str]:
    """Deriva as URLs de administracao (asyncpg puro, para CREATE DATABASE) e de teste
    a partir da DATABASE_URL de desenvolvimento, apenas trocando o nome do banco."""
    base_url = get_settings().database_url.removeprefix("postgresql+asyncpg://")
    credentials_host, _, dev_db_name = base_url.rpartition("/")
    admin_url = f"postgresql://{credentials_host}/{dev_db_name}"
    test_url = f"postgresql+asyncpg://{credentials_host}/{_TEST_DB_NAME}"
    return admin_url, test_url


async def _garantir_banco_teste_existe() -> str:
    admin_url, test_url = _admin_url_and_test_url()
    conn = await asyncpg.connect(admin_url)
    try:
        existe = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", _TEST_DB_NAME
        )
        if not existe:
            await conn.execute(f'CREATE DATABASE "{_TEST_DB_NAME}"')
    finally:
        await conn.close()
    return test_url


@pytest_asyncio.fixture
async def test_engine() -> AsyncIterator[AsyncEngine]:
    """Um engine novo por teste - pytest-asyncio abre um event loop por funcao de teste, e
    conexoes asyncpg nao podem ser reaproveitadas entre loops diferentes. create_all e
    idempotente (nao recria tabelas ja existentes), entao o custo extra e minimo."""
    test_url = await _garantir_banco_teste_existe()
    engine = create_async_engine(test_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    """Cada teste usa UUIDs proprios (clinica/paciente novos), entao registros de testes
    anteriores nao interferem - dispensa rollback transacional complexo entre testes."""
    session_factory = async_sessionmaker(test_engine, expire_on_commit=False)

    async with session_factory() as session:
        yield session
