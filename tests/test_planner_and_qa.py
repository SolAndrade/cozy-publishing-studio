import unittest

from backend.domain.states import QAResult
from backend.planners.rubric import ConceptScore
from backend.planners.series_planner import BookConcept, select_five
from backend.production.qa import decide_qa


def score(total_bias: int = 0) -> ConceptScore:
    base = max(1, min(5, 3 + total_bias))
    return ConceptScore(base, base, base, base, base, base)


class PlannerTests(unittest.TestCase):
    def test_selects_exactly_five(self):
        concepts = [BookConcept(f"Book {i}", "Premise", score(i % 3 - 1)) for i in range(8)]
        selected = select_five(concepts)
        self.assertEqual(len(selected), 5)
        self.assertGreaterEqual(selected[0].score.total, selected[-1].score.total)


class QATests(unittest.TestCase):
    def test_pass_by_default(self):
        self.assertEqual(decide_qa().result, QAResult.PASS)

    def test_structural_failure_regenerates(self):
        self.assertEqual(decide_qa(structural_failure=True).result, QAResult.REGENERATE)

    def test_local_issue_routes_fix(self):
        self.assertEqual(decide_qa(localized_material_issue=True).result, QAResult.FIX_LOCAL)


if __name__ == "__main__":
    unittest.main()
