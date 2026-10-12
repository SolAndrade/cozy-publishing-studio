from dataclasses import dataclass

from backend.domain.states import QAResult


@dataclass(frozen=True, slots=True)
class QADecision:
    result: QAResult
    reason: str = ""

    @property
    def should_stop(self) -> bool:
        return self.result != QAResult.PASS


def decide_qa(*, structural_failure: bool = False, localized_material_issue: bool = False) -> QADecision:
    """Deterministic routing after semantic/visual checks have produced flags."""
    if structural_failure:
        return QADecision(QAResult.REGENERATE, "Concrete structural/material failure")
    if localized_material_issue:
        return QADecision(QAResult.FIX_LOCAL, "Localized material issue")
    return QADecision(QAResult.PASS)
