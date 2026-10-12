from dataclasses import dataclass

from backend.domain.models import Book, Scene, Series
from backend.domain.project import PublishingProject
from backend.domain.states import BookState


@dataclass(slots=True)
class ProductionEngine:
    """Pure orchestration core. External AI/storage adapters plug in later."""

    def create_series(self, name: str, concepts: list[tuple[str, str]]) -> PublishingProject:
        if len(concepts) != 5:
            raise ValueError("Production requires exactly five approved book concepts")
        books = [
            Book(title=title.strip(), subtitle=subtitle.strip(), position=index)
            for index, (title, subtitle) in enumerate(concepts, start=1)
        ]
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

    def start_generation(self, book: Book) -> None:
        if len(book.scenes) != 40:
            raise ValueError("Generation requires a complete 40-scene manifest")
        book.advance(BookState.GENERATING)
