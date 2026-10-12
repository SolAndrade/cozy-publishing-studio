import unittest

from backend.domain.states import BookState
from backend.kdp.operator import KDPOperator
from backend.prepress.validator import ImageSpec, validate_image_spec
from backend.publishing.gate import PublicationGate


class PrepressTests(unittest.TestCase):
    def test_good_square_master(self):
        self.assertEqual(validate_image_spec(ImageSpec(2400, 2400, 7.5, 7.5)), [])

    def test_low_resolution_fails(self):
        issues = validate_image_spec(ImageSpec(1000, 1000, 7.5, 7.5))
        self.assertTrue(any("resolution" in issue.lower() for issue in issues))


class PublishingTests(unittest.TestCase):
    def test_gate_requires_all_assets(self):
        result = PublicationGate().check(
            book_state=BookState.KDP_DRAFT_READY,
            interior_ready=True,
            cover_ready=False,
            metadata_ready=True,
            ai_declaration_ready=True,
        )
        self.assertFalse(result.ready)
        self.assertIn("Cover is not locked", result.blockers)

    def test_operator_never_auto_publishes(self):
        with self.assertRaises(RuntimeError):
            KDPOperator().publish("book-1")


if __name__ == "__main__":
    unittest.main()
