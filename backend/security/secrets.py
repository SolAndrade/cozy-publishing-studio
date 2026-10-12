import os
from dataclasses import dataclass


@dataclass(frozen=True,slots=True)
class SecretStatus:
    name: str
    configured: bool


def secret_status(names: tuple[str,...]) -> tuple[SecretStatus,...]:
    return tuple(SecretStatus(name,bool(os.getenv(name,"").strip())) for name in names)


def require_secret(name: str) -> str:
    value=os.getenv(name,"").strip()
    if not value:
        raise RuntimeError(f"Missing required server-side secret: {name}")
    return value
