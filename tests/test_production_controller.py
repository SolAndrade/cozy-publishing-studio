import unittest

from backend.domain.states import BookState, QAResult
from backend.orchestrator.engine import ProductionEngine
from backend.production.controller import ProductionController
from backend.jobs.queue import InMemoryJobQueue


class ControllerTests(unittest.TestCase):
    def make_book(self):
        engine=ProductionEngine()
        project=engine.create_series("S", [(f"B{i}", "", "Locked visual identity") for i in range(1,6)])
        book=project.series.books[0]
        engine.install_manifest(book, [f"Scene {i}" for i in range(1,41)])
        engine.start_generation(book)
        return project, book

    def test_next_scene_job(self):
        project,book=self.make_book()
        controller=ProductionController(InMemoryJobQueue())
        job=controller.enqueue_next_scene(project.id,book)
        self.assertEqual(job.payload["scene_number"],1)

    def test_skips_locked_scene(self):
        project,book=self.make_book()
        book.scenes[0].record_generation()
        book.scenes[0].qa(QAResult.PASS)
        controller=ProductionController(InMemoryJobQueue())
        job=controller.enqueue_next_scene(project.id,book)
        self.assertEqual(job.payload["scene_number"],2)

    def test_all_locked_advances_book(self):
        project,book=self.make_book()
        for scene in book.scenes:
            scene.record_generation()
            scene.qa(QAResult.PASS)
        controller=ProductionController(InMemoryJobQueue())
        self.assertIsNone(controller.enqueue_next_scene(project.id,book))
        self.assertEqual(book.state,BookState.ART_LOCKED)


if __name__=="__main__":
    unittest.main()
