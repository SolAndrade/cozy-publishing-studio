from dataclasses import dataclass, field

from .errors import GenerationLimitError, InvalidTransitionError, LockedAssetError
from .states import BookState, QAResult, SceneState


BOOK_FLOW = [
    BookState.SERIES_PLANNED,
    BookState.BOOK_PLANNED,
    BookState.GENERATING,
    BookState.ART_LOCKED,
    BookState.PREPRESS_PASS,
    BookState.INTERIOR_LOCKED,
    BookState.COVER_LOCKED,
    BookState.METADATA_READY,
    BookState.KDP_DRAFT_READY,
    BookState.HUMAN_APPROVAL,
    BookState.PUBLISHED,
]


@dataclass(slots=True)
class Scene:
    number: int
    title: str
    state: SceneState = SceneState.PLANNED
    generations: int = 0
    qa_result: QAResult | None = None
    material_defect: str | None = None

    def record_generation(self) -> None:
        if self.state == SceneState.ART_LOCKED:
            raise LockedAssetError(f"Scene {self.number} is ART_LOCKED")
        if self.generations >= 2 and not self.material_defect:
            raise GenerationLimitError(
                "A third generation requires a recorded concrete material defect"
            )
        self.generations += 1
        self.state = SceneState.GENERATED
        self.qa_result = None

    def record_material_defect(self, defect: str) -> None:
        defect = defect.strip()
        if not defect:
            raise ValueError("Material defect must be concrete and non-empty")
        self.material_defect = defect

    def qa(self, result: QAResult) -> None:
        if self.state != SceneState.GENERATED:
            raise InvalidTransitionError("QA requires a GENERATED scene")
        self.qa_result = result
        if result == QAResult.PASS:
            self.state = SceneState.ART_LOCKED
            self.material_defect = None

    @property
    def locked(self) -> bool:
        return self.state == SceneState.ART_LOCKED


@dataclass(slots=True)
class Book:
    title: str
    subtitle: str
    position: int
    locked_brief: str = ""
    scenes: list[Scene] = field(default_factory=list)
    state: BookState = BookState.SERIES_PLANNED

    def advance(self, target: BookState) -> None:
        current_index = BOOK_FLOW.index(self.state)
        target_index = BOOK_FLOW.index(target)
        if target_index != current_index + 1:
            raise InvalidTransitionError(
                f"Cannot transition {self.state} directly to {target}"
            )
        if target == BookState.ART_LOCKED:
            if len(self.scenes) != 40 or not all(scene.locked for scene in self.scenes):
                raise InvalidTransitionError(
                    "ART_LOCKED requires exactly 40 locked scenes"
                )
        self.state = target


@dataclass(slots=True)
class Series:
    name: str
    books: list[Book]

    def __post_init__(self) -> None:
        if len(self.books) != 5:
            raise ValueError("A production series must contain exactly 5 books")
        positions = sorted(book.position for book in self.books)
        if positions != [1, 2, 3, 4, 5]:
            raise ValueError("Series book positions must be exactly 1..5")
