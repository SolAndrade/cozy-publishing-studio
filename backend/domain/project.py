from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from backend.domain.models import Book, Series


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class PublishingProject:
    series: Series
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    def touch(self) -> None:
        self.updated_at = utc_now()

    def to_dict(self) -> dict:
        return asdict(self)
