from abc import abstractmethod

from backend.domain.entities.refresh_token import RefreshToken
from backend.domain.repositories.base_repository import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    @abstractmethod
    async def buscar_por_token_hash(self, token_hash: str) -> RefreshToken | None: ...

    @abstractmethod
    async def revogar(self, token_hash: str) -> None: ...
