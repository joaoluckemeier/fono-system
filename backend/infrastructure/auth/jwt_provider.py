import hashlib
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

from jose import JWTError, jwt

from backend.config import Settings


@dataclass
class AccessTokenPayload:
    usuario_id: UUID
    clinica_id: UUID
    papel: str


class TokenInvalidoError(Exception):
    pass


class JWTProvider:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def criar_access_token(self, usuario_id: UUID, clinica_id: UUID, papel: str) -> str:
        agora = datetime.now(UTC)
        payload = {
            "sub": str(usuario_id),
            "clinica_id": str(clinica_id),
            "papel": papel,
            "iat": agora,
            "exp": agora + timedelta(minutes=self._settings.jwt_access_token_expire_minutes),
        }
        return jwt.encode(payload, self._settings.jwt_secret, algorithm=self._settings.jwt_algorithm)

    def decodificar_access_token(self, token: str) -> AccessTokenPayload:
        try:
            payload = jwt.decode(
                token, self._settings.jwt_secret, algorithms=[self._settings.jwt_algorithm]
            )
        except JWTError as exc:
            raise TokenInvalidoError("Token invalido ou expirado") from exc

        return AccessTokenPayload(
            usuario_id=UUID(payload["sub"]),
            clinica_id=UUID(payload["clinica_id"]),
            papel=payload["papel"],
        )

    def gerar_refresh_token_expiracao(self) -> datetime:
        return datetime.now(UTC) + timedelta(days=self._settings.jwt_refresh_token_expire_days)

    @staticmethod
    def gerar_refresh_token_raw() -> str:
        return secrets.token_urlsafe(48)

    @staticmethod
    def hash_refresh_token(token_raw: str) -> str:
        return hashlib.sha256(token_raw.encode()).hexdigest()
