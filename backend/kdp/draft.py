from dataclasses import dataclass

from backend.metadata.package import MetadataPackage


@dataclass(slots=True)
class DraftPackage:
    metadata: MetadataPackage
    interior_path: str
    cover_path: str
    final_human_approval_required: bool = True

    def validate(self) -> None:
        self.metadata.validate()
        if not self.interior_path or not self.cover_path:
            raise ValueError("Interior and cover are required")
        if not self.final_human_approval_required:
            raise ValueError("Final publication must require human approval")
