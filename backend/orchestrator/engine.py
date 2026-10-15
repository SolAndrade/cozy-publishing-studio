from dataclasses import dataclass

from backend.domain.models import Book, Scene, Series
from backend.domain.project import PublishingProject
from backend.domain.states import BookState


@dataclass(slots=True)
class ProductionEngine:
    """Pure orchestration core. External AI/storage adapters plug in later."""

    def create_series(
        self, name: str, concepts: list[tuple[str, str] | tuple[str, str, str]]
    ) -> PublishingProject:
        if len(concepts) != 5:
            raise ValueError("Production requires exactly five approved book concepts")
        books = []
        for index, concept in enumerate(concepts, start=1):
            if len(concept) == 2:
                title, subtitle = concept
                locked_brief = ""
            elif len(concept) == 3:
                title, subtitle, locked_brief = concept
            else:
                raise ValueError(
                    "Each book concept requires title/subtitle and optional locked brief"
                )
            books.append(
                Book(
                    title=title.strip(),
                    subtitle=subtitle.strip(),
                    position=index,
                    locked_brief=locked_brief.strip(),
                )
            )
        return PublishingProject(Series(name=name.strip(), books=books))

    def install_manifest(self, book: Book, scenes: list[str]) -> None:
        if book.state != BookState.SERIES_PLANNED:
            raise ValueError("Manifest can only be installed on a newly planned book")
        if len(scenes) != 40:
            raise ValueError("A coloring book manifest must contain exactly 40 scenes")
        if len({scene.casefold().strip() for scene in scenes}) != 40:
            raise ValueError("Scene titles must be unique")
        book.scenes = [Scene(i, title.strip()) for i, title in enumerate(scenes, 1)]
        book.advance(BookState.BOOK_PLANNED)

    def set_locked_brief(self, book: Book, locked_brief: str) -> None:
        if book.state not in {BookState.SERIES_PLANNED, BookState.BOOK_PLANNED}:
            raise ValueError("Locked visual brief cannot change after generation starts")
        locked_brief = locked_brief.strip()
        if not locked_brief:
            raise ValueError("Locked visual brief cannot be empty")
        book.locked_brief = locked_brief

    def start_generation(self, book: Book) -> None:
        if len(book.scenes) != 40:
            raise ValueError("Generation requires a complete 40-scene manifest")
        if not book.locked_brief.strip():
            raise ValueError("Generation requires a locked visual brief")
        book.advance(BookState.GENERATING)
