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


def provider_status() -> tuple[ProviderStatus,...]:
    image=os.getenv("COZY_IMAGE_PROVIDER","mock")
    vision=os.getenv("COZY_VISION_PROVIDER","mock")
    storage=os.getenv("COZY_ARTIFACT_STORE","local")
    def state(role,name):
        if name in ("mock","local"):
            return ProviderStatus(role,name,ProviderState.MOCK,"Development adapter; not production cloud")
        key=f"COZY_{role.upper()}_API_KEY"
        configured=bool(os.getenv(key,"").strip())
        return ProviderStatus(role,name,ProviderState.CONFIGURED if configured else ProviderState.BLOCKED,
                              "Server-side secret configured" if configured else f"Missing {key}")
    return (state("image",image),state("vision",vision),state("storage",storage))
