import importlib
import os,unittest
from unittest.mock import patch
from backend.api.app import book_payload, series_concepts, start_book_generation
from backend.api.status import system_status


class APIStatusTests(unittest.TestCase):
    def test_status_never_exposes_secret_values(self):
        with patch.dict(os.environ,{"OPENAI_API_KEY":"super-secret-openai"},clear=True):
            payload=system_status()
            rendered=str(payload)
            self.assertNotIn("super-secret-openai",rendered)
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

    def test_generation_start_rolls_back_state_when_enqueue_fails(self):
        from backend.api import app
        from backend.domain.states import BookState
        from backend.orchestrator.engine import ProductionEngine
        from backend.runtime import Runtime

        local_runtime = Runtime()
        local_engine = ProductionEngine()
        project = local_runtime.add(
            local_engine.create_series(
                "Series",
                [
                    (f"Book {i}", "", f"Visual identity {i}")
                    for i in range(1, 6)
                ],
            )
        )
        book = project.series.books[0]
        local_engine.install_manifest(book, [f"Scene {i}" for i in range(1, 41)])

        class FailingProduction:
            def enqueue_next_scene(self, project_id, target_book):
                raise RuntimeError("queue_unavailable")

        class FailingRuntime:
            production = FailingProduction()

            def persist(self, target_project):
                raise AssertionError("failed start must not persist")

        original_engine, original_runtime = app.engine, app.runtime
        app.engine, app.runtime = local_engine, FailingRuntime()
        try:
            with self.assertRaisesRegex(RuntimeError, "queue_unavailable"):
                start_book_generation(project, book)
        finally:
            app.engine, app.runtime = original_engine, original_runtime

        self.assertEqual(book.state, BookState.BOOK_PLANNED)

    def test_api_module_imports(self):
        module=importlib.import_module("backend.api.app")
        self.assertTrue(hasattr(module,"Handler"))


if __name__=="__main__": unittest.main()
