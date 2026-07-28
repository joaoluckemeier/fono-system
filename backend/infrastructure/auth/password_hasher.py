from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

_ph = PasswordHasher()


def hash_senha(senha_plain: str) -> str:
    return _ph.hash(senha_plain)


def verificar_senha(senha_hash: str, senha_plain: str) -> bool:
    try:
        return _ph.verify(senha_hash, senha_plain)
    except VerifyMismatchError:
        return False
