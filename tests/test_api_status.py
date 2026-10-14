import importlib
import os,unittest
from unittest.mock import patch
from backend.api.app import book_payload, series_concepts
from backend.api.status import system_status


class APIStatusTests(unittest.TestCase):
    def test_status_never_exposes_secret_values(self):
        with patch.dict(os.environ,{"COZY_IMAGE_API_KEY":"super-secret","COZY_VISION_API_KEY":"vision-secret"},clear=True):
            payload=system_status()
            rendered=str(payload)
            self.assertNotIn("super-secret",rendered)
            self.assertNotIn("vision-secret",rendered)
            self.assertTrue(all("configured" in x for x in payload["secrets"]))

    def test_series_payload_preserves_explicit_locked_brief(self):
        concepts = series_concepts(
            {
                "books": [
                    {
                        "title": "Village Corners",
                        "subtitle": "A cozy coloring book",
                        "locked_brief": "European village line-art identity",
                    }
                ]
            }
        )
        self.assertEqual(
            concepts[0],
            (
                "Village Corners",
                "A cozy coloring book",
                "European village line-art identity",
            ),
        )

    def test_series_payload_does_not_promote_subtitle_to_locked_brief(self):
        concepts = series_concepts(
            {"books": [{"title": "Village Corners", "subtitle": "Marketing subtitle"}]}
        )
        self.assertEqual(concepts[0], ("Village Corners", "Marketing subtitle", ""))

    def test_book_payload_exposes_locked_brief(self):
        from backend.domain.models import Book

        payload = book_payload(
            Book(
                title="Village Corners",
                subtitle="A cozy coloring book",
                position=1,
                locked_brief="European village line-art identity",
            )
        )
        self.assertEqual(
            payload["locked_brief"], "European village line-art identity"
        )

    def test_api_module_imports(self):
        module=importlib.import_module("backend.api.app")
        self.assertTrue(hasattr(module,"Handler"))


if __name__=="__main__": unittest.main()
