from dataclasses import dataclass, field


@dataclass(slots=True)
class MetadataPackage:
    title: str
    subtitle: str
    description: str
    keywords: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    ai_generated_content: bool = True

    def validate(self) -> None:
        if not self.title.strip():
            raise ValueError("Title is required")
        if len(self.keywords) > 7:
            raise ValueError("At most 7 keyword fields are supported by this studio policy")
        if any(not keyword.strip() for keyword in self.keywords):
            raise ValueError("Keywords cannot be blank")
