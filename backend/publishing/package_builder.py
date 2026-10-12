from dataclasses import dataclass
from pathlib import Path

from backend.metadata.editorial import EditorialMetadata


@dataclass(frozen=True,slots=True)
class PublishingBundle:
    interior_pdf: str
    cover_pdf: str
    metadata: EditorialMetadata
    ready: bool
    issues: tuple[str,...]


def build_publishing_bundle(interior_pdf: str,cover_pdf: str,metadata: EditorialMetadata) -> PublishingBundle:
    issues=[]
    for label,path in (("interior",interior_pdf),("cover",cover_pdf)):
        p=Path(path)
        if not p.exists() or p.stat().st_size==0: issues.append(f"Missing {label} PDF")
    try: metadata.validate()
    except ValueError as exc: issues.append(str(exc))
    return PublishingBundle(interior_pdf,cover_pdf,metadata,not issues,tuple(issues))
