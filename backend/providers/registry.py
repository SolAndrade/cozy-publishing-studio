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


PROVIDER_SECRETS = {
    "image": "COZY_IMAGE_API_KEY",
    "vision": "COZY_VISION_API_KEY",
    "storage": "COZY_STORAGE_API_KEY",
}


def provider_status() -> tuple[ProviderStatus,...]:
    image=os.getenv("COZY_IMAGE_PROVIDER","mock").strip() or "mock"
    vision=os.getenv("COZY_VISION_PROVIDER","mock").strip() or "mock"
    storage=os.getenv("COZY_ARTIFACT_STORE","local").strip() or "local"

    def state(role,name):
        if name in ("mock","local"):
            return ProviderStatus(role,name,ProviderState.MOCK,"Development adapter; not production cloud")
        key=PROVIDER_SECRETS[role]
        configured=bool(os.getenv(key,"").strip())
        return ProviderStatus(
            role,name,
            ProviderState.CONFIGURED if configured else ProviderState.BLOCKED,
            "Server-side secret configured" if configured else f"Missing {key}",
        )

    return (state("image",image),state("vision",vision),state("storage",storage))
