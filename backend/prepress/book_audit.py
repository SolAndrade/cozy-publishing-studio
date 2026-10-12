from dataclasses import dataclass

from backend.domain.models import Book


@dataclass(frozen=True,slots=True)
class BookAudit:
    passed: bool
    issues: tuple[str,...]


def audit_book(book: Book) -> BookAudit:
    issues=[]
    if len(book.scenes)!=40:
        issues.append("Book must contain exactly 40 scenes")
    titles=[s.title.casefold().strip() for s in book.scenes]
    if len(titles)!=len(set(titles)):
        issues.append("Duplicate scene titles detected")
    unlocked=[s.number for s in book.scenes if not s.locked]
    if unlocked:
        issues.append(f"Unlocked scenes remain: {unlocked}")
    over_generated=[s.number for s in book.scenes if s.generations>2 and not s.material_defect]
    if over_generated:
        issues.append(f"Generation policy violation: {over_generated}")
    return BookAudit(not issues,tuple(issues))
