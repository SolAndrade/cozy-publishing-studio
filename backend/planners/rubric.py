from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ConceptScore:
    differentiation: int
    visual_potential: int
    colorability: int
    series_fit: int
    commercial_interest: int
    feasibility: int

    def __post_init__(self) -> None:
        values = (
            self.differentiation,
            self.visual_potential,
            self.colorability,
            self.series_fit,
            self.commercial_interest,
            self.feasibility,
        )
        if any(value < 1 or value > 5 for value in values):
            raise ValueError("Every rubric score must be between 1 and 5")

    @property
    def total(self) -> int:
        return sum(
            (
                self.differentiation,
                self.visual_potential,
                self.colorability,
                self.series_fit,
                self.commercial_interest,
                self.feasibility,
            )
        )
