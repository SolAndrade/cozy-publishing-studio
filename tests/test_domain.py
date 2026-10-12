import unittest

from backend.domain.errors import GenerationLimitError, InvalidTransitionError, LockedAssetError
from backend.domain.models import Book, Scene, Series
from backend.domain.states import BookState, QAResult, SceneState


class SceneTests(unittest.TestCase):
    def test_pass_locks_scene(self):
        scene = Scene(1, "Classic Window Café")
        scene.record_generation()
        scene.qa(QAResult.PASS)
        self.assertEqual(scene.state, SceneState.ART_LOCKED)
        self.assertTrue(scene.locked)

    def test_locked_scene_cannot_regenerate(self):
        scene = Scene(1, "Classic Window Café")
        scene.record_generation()
        scene.qa(QAResult.PASS)
        with self.assertRaises(LockedAssetError):
            scene.record_generation()

    def test_third_generation_requires_material_defect(self):
        scene = Scene(1, "Classic Window Café")
        scene.record_generation()
        scene.qa(QAResult.REGENERATE)
        scene.record_generation()
        scene.qa(QAResult.REGENERATE)
        with self.assertRaises(GenerationLimitError):
            scene.record_generation()
        scene.record_material_defect("Broken perspective in the main window")
        scene.record_generation()
        self.assertEqual(scene.generations, 3)


class BookTests(unittest.TestCase):
    def test_cannot_skip_book_state(self):
        book = Book("Book", "Subtitle", 1)
        with self.assertRaises(InvalidTransitionError):
            book.advance(BookState.GENERATING)

    def test_art_lock_requires_40_locked_scenes(self):
        scenes = [Scene(i, f"Scene {i}") for i in range(1, 41)]
        book = Book("Book", "Subtitle", 1, scenes=scenes)
        book.advance(BookState.BOOK_PLANNED)
        book.advance(BookState.GENERATING)
        with self.assertRaises(InvalidTransitionError):
            book.advance(BookState.ART_LOCKED)


class SeriesTests(unittest.TestCase):
    def test_series_requires_five_books(self):
        books = [Book(f"Book {i}", "Subtitle", i) for i in range(1, 6)]
        series = Series("Cozy Little Worlds", books)
        self.assertEqual(len(series.books), 5)

        with self.assertRaises(ValueError):
            Series("Bad Series", books[:4])


if __name__ == "__main__":
    unittest.main()
