from dataclasses import dataclass
from enum import StrEnum
import os


class ProviderState(StrEnum):
    MOCK="MOCK"
    CONFIGURED="CONFIGURED"
    BLOCKED="BLOCKED"


@dataclass(frozen=True,slots=True)
class ProviderStatus:
    role: str
    provider: str
    state: ProviderState
    detail: str


def _generic_provider(role: str, name: str) -> ProviderStatus:
    if name == "mock":
        return ProviderStatus(role,name,ProviderState.MOCK,"Development adapter; not production cloud")
    configured=name=="openai" and bool(os.getenv("OPENAI_API_KEY","").strip())
    return ProviderStatus(
        role,name,
        ProviderState.CONFIGURED if configured else ProviderState.BLOCKED,
        "Server-side secret configured" if configured else "Adapter unavailable or OPENAI_API_KEY missing",
    )


def _storage_status(name: str) -> ProviderStatus:
    if name == "local":
        return ProviderStatus(
            "storage",name,ProviderState.MOCK,
            "Development adapter; not durable shared production storage",
        )
    if name == "s3":
        bucket=bool(os.getenv("COZY_S3_BUCKET","").strip())
        access=bool(os.getenv("AWS_ACCESS_KEY_ID","").strip())
        secret=bool(os.getenv("AWS_SECRET_ACCESS_KEY","").strip())
        configured=bucket and access and secret
        return ProviderStatus(
            "storage",name,
            ProviderState.CONFIGURED if configured else ProviderState.BLOCKED,
            "Private S3-compatible storage configured"
            if configured else "Missing COZY_S3_BUCKET or AWS S3 credentials",
        )
    return ProviderStatus(
        "storage",name,ProviderState.BLOCKED,
        "Storage adapter is not implemented",
    )


def provider_status() -> tuple[ProviderStatus,...]:
    image=(os.getenv("COZY_IMAGE_PROVIDER","mock").strip() or "mock").lower()
    vision=(os.getenv("COZY_VISION_PROVIDER","mock").strip() or "mock").lower()
    storage=(os.getenv("COZY_ARTIFACT_STORE","local").strip() or "local").lower()
    return (
        _generic_provider("image",image),
        _generic_provider("vision",vision),
        _storage_status(storage),
    )
