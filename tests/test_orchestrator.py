import unittest

from backend.domain.states import BookState
from backend.orchestrator.engine import ProductionEngine


class OrchestratorTests(unittest.TestCase):
    def test_create_series_and_install_manifest(self):
        engine = ProductionEngine()
        concepts = [(f"Book {i}", f"Subtitle {i}") for i in range(1, 6)]
        project = engine.create_series("Series", concepts)
        self.assertEqual(len(project.series.books), 5)

        book = project.series.books[0]
        engine.install_manifest(book, [f"Scene {i}" for i in range(1, 41)])
        self.assertEqual(book.state, BookState.BOOK_PLANNED)
        self.assertEqual(len(book.scenes), 40)

        engine.start_generation(book)
        self.assertEqual(book.state, BookState.GENERATING)

    def test_manifest_rejects_duplicates(self):
        engine = ProductionEngine()
        project = engine.create_series("Series", [(f"B{i}", "S") for i in range(5)])
        with self.assertRaises(ValueError):
            engine.install_manifest(project.series.books[0], ["Same"] * 40)


if __name__ == "__main__":
    unittest.main()
