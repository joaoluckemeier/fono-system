import pytest

from backend.config import Settings


@pytest.fixture
def settings() -> Settings:
    return Settings(
        database_url="postgresql+asyncpg://fono:fono@localhost:5433/fono_test",
        jwt_secret="test-secret-nao-usar-em-producao",
        minio_endpoint="localhost:9000",
        minio_access_key="minioadmin",
        minio_secret_key="minioadmin",
        minio_bucket="fono-anexos-test",
        redis_url="redis://localhost:6379/1",
    )
