from abc import ABC, abstractmethod


class StorageServiceInterface(ABC):
    """O dominio nao sabe se o anexo vai pro MinIO local ou pra S3 - so chama a interface."""

    @abstractmethod
    async def salvar(self, conteudo: bytes, nome_arquivo: str) -> str:
        """Persiste o conteudo e retorna o storage_ref opaco (ex: minio://{bucket}/{key})."""

    @abstractmethod
    async def obter_url(self, storage_ref: str) -> str: ...

    @abstractmethod
    async def deletar(self, storage_ref: str) -> None: ...
