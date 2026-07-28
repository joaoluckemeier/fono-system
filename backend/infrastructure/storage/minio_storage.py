import asyncio
import io
import uuid

from minio import Minio

from backend.config import Settings
from backend.domain.services.storage_service import StorageServiceInterface


class MinIOStorageService(StorageServiceInterface):
    """O cliente oficial do MinIO e sincrono - as chamadas rodam em thread pool
    (asyncio.to_thread) para nao bloquear o event loop do FastAPI."""

    def __init__(self, settings: Settings) -> None:
        self._bucket = settings.minio_bucket
        self._client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )
        if not self._client.bucket_exists(self._bucket):
            self._client.make_bucket(self._bucket)

    async def salvar(self, conteudo: bytes, nome_arquivo: str) -> str:
        key = f"{uuid.uuid4()}-{nome_arquivo}"
        await asyncio.to_thread(
            self._client.put_object, self._bucket, key, io.BytesIO(conteudo), length=len(conteudo)
        )
        return f"minio://{self._bucket}/{key}"

    async def obter_url(self, storage_ref: str) -> str:
        key = storage_ref.removeprefix(f"minio://{self._bucket}/")
        return await asyncio.to_thread(self._client.presigned_get_object, self._bucket, key)

    async def deletar(self, storage_ref: str) -> None:
        key = storage_ref.removeprefix(f"minio://{self._bucket}/")
        await asyncio.to_thread(self._client.remove_object, self._bucket, key)
