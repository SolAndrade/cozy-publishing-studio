from dataclasses import dataclass


@dataclass(frozen=True,slots=True)
class EditorialMetadata:
    title: str
    subtitle: str
    series_name: str|None
    series_position: int|None
    description: str
    keywords: tuple[str,...]
    categories: tuple[str,...]
    ai_generated_content: bool

    def validate(self):
        if not self.title.strip(): raise ValueError("Title is required")
        if len(self.keywords)>7: raise ValueError("At most 7 keyword fields are supported by this workflow")
        if any(not x.strip() for x in self.keywords): raise ValueError("Keywords cannot be blank")
        if not self.description.strip(): raise ValueError("Description is required")
        if not self.categories: raise ValueError("At least one category is required")
        return self
