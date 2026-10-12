from dataclasses import dataclass

from .rubric import ConceptScore


@dataclass(frozen=True, slots=True)
class BookConcept:
    title: str
    premise: str
    score: ConceptScore


def select_five(concepts: list[BookConcept]) -> list[BookConcept]:
    """Return exactly five strongest viable concepts without model debate loops."""
    if len(concepts) < 5:
        raise ValueError("At least five candidate concepts are required")
    unique: dict[str, BookConcept] = {}
    for concept in concepts:
        key = concept.title.casefold().strip()
        current = unique.get(key)
        if current is None or concept.score.total > current.score.total:
            unique[key] = concept
    ranked = sorted(unique.values(), key=lambda item: item.score.total, reverse=True)
    if len(ranked) < 5:
        raise ValueError("At least five unique concepts are required")
    return ranked[:5]
