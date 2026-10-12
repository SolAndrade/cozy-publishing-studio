from dataclasses import dataclass
from enum import StrEnum


class KDPCapability(StrEnum):
    PACKAGE_ONLY = "PACKAGE_ONLY"
    DRAFT_AUTOMATION = "DRAFT_AUTOMATION"


@dataclass(slots=True)
class KDPOperator:
    """Safety boundary for KDP.

    PACKAGE_ONLY is the default until an authorized, reliable draft mechanism is
    configured. Final publication is deliberately not exposed as an automated action.
    """
    capability: KDPCapability = KDPCapability.PACKAGE_ONLY

    def prepare(self, package_id: str) -> dict:
        return {"package_id": package_id, "status": "READY_FOR_KDP"}

    def create_draft(self, package_id: str) -> dict:
        if self.capability != KDPCapability.DRAFT_AUTOMATION:
            raise RuntimeError("KDP draft automation is not configured")
        return {"package_id": package_id, "status": "DRAFT_CREATED"}

    def publish(self, package_id: str) -> None:
        raise RuntimeError("Automatic final publication is intentionally disabled")
