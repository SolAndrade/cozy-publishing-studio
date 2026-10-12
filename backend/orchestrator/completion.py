from backend.domain.models import Book
from backend.domain.states import BookState


def advance_after_art(book: Book,book_audit_passed: bool):
    if book.state!=BookState.ART_LOCKED: raise ValueError("Book must be ART_LOCKED")
    if not book_audit_passed: raise ValueError("Whole-book audit must pass")
    book.advance(BookState.PREPRESS_PASS)


def advance_after_interior(book: Book,preflight_passed: bool):
    if book.state!=BookState.PREPRESS_PASS: raise ValueError("Book must be PREPRESS_PASS")
    if not preflight_passed: raise ValueError("Interior preflight must pass")
    book.advance(BookState.INTERIOR_LOCKED)


def advance_after_cover(book: Book,preflight_passed: bool):
    if book.state!=BookState.INTERIOR_LOCKED: raise ValueError("Book must be INTERIOR_LOCKED")
    if not preflight_passed: raise ValueError("Cover preflight must pass")
    book.advance(BookState.COVER_LOCKED)


def advance_after_metadata(book: Book,metadata_valid: bool):
    if book.state!=BookState.COVER_LOCKED: raise ValueError("Book must be COVER_LOCKED")
    if not metadata_valid: raise ValueError("Metadata must validate")
    book.advance(BookState.METADATA_READY)
