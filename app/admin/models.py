from dataclasses import dataclass
from hashlib import sha256
from typing import Self

from aiohttp_session import Session


@dataclass
class Admin:
    id: int
    email: str
    password: str | None = None

    def is_password_valid(self, password: str) -> bool:
        return self.password == sha256(password.encode()).hexdigest()

    @classmethod
    def from_session(cls, session: Session) -> Self:
        return cls(id=session["admin"]["id"], email=session["admin"]["email"])
