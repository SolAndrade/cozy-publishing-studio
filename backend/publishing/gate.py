from dataclasses import dataclass

from backend.domain.states import BookState


@dataclass(frozen=True, slots=True)
class PublicationReadiness:
    ready: bool
    blockers: tuple[str, ...]


class PublicationGate:
    def check(self, *, book_state: BookState, interior_ready: bool, cover_ready: bool,
              metadata_ready: bool, ai_declaration_ready: bool) -> PublicationReadiness:
        blockers: list[str] = []
        if book_state not in {BookState.KDP_DRAFT_READY, BookState.HUMAN_APPROVAL}:
            blockers.append("Book has not reached KDP draft stage")
        if not interior_ready:
            blockers.append("Interior is not locked")
        if not cover_ready:
            blockers.append("Cover is not locked")
        if not metadata_ready:
            blockers.append("Metadata is incomplete")
        if not ai_declaration_ready:
            blockers.append("AI-content declaration is incomplete")
        return PublicationReadiness(not blockers, tuple(blockers))
