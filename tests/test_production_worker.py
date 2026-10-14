import tempfile
import unittest

from backend.domain.states import BookState
from backend.orchestrator.engine import ProductionEngine
from backend.providers.mock import MockImageGenerator, MockVisualReviewer
from backend.runtime import Runtime
from backend.storage.artifact_store import LocalArtifactStore
from backend.workers.production_worker import ProductionWorker
from backend.workers.runner import Worker


class ProductionWorkerTests(unittest.TestCase):
    def test_mock_pipeline_locks_all_40(self):
        engine=ProductionEngine()
        runtime=Runtime()
        project=runtime.add(engine.create_series("S",[(f"B{i}","") for i in range(1,6)]))
        book=project.series.books[0]
        engine.install_manifest(book,[f"Scene {i}" for i in range(1,41)])
        engine.start_generation(book)
        runtime.production.enqueue_next_scene(project.id,book)
        with tempfile.TemporaryDirectory() as d:
            production=ProductionWorker(
                runtime,
                MockImageGenerator(f"{d}/generated"),
                MockVisualReviewer(),
                LocalArtifactStore(f"{d}/artifacts"),
            )
            worker=Worker(runtime.queue,production.handlers())
            for _ in range(100):
                if worker.run_one() is None:
                    break
        self.assertEqual(sum(s.locked for s in book.scenes),40)
        self.assertEqual(book.state,BookState.ART_LOCKED)


    def test_pass_without_durable_artifact_does_not_lock_scene(self):
        engine = ProductionEngine()
        runtime = Runtime()
        project = runtime.add(engine.create_series("S", [(f"B{i}", "") for i in range(1, 6)]))
        book = project.series.books[0]
        engine.install_manifest(book, [f"Scene {i}" for i in range(1, 41)])
        engine.start_generation(book)
        scene = book.scenes[0]

        class PassingReviewer:
            def review(self, image_path, title):
                return {"result": "PASS", "reason": ""}

        with tempfile.TemporaryDirectory() as d:
            production = ProductionWorker(
                runtime,
                MockImageGenerator(f"{d}/generated"),
                PassingReviewer(),
                LocalArtifactStore(f"{d}/artifacts"),
            )
            with self.assertRaisesRegex(RuntimeError, "approved_scene_requires_durable_artifact"):
                production.review({
                    "project_id": project.id,
                    "book_position": book.position,
                    "scene_number": scene.number,
                    "image_path": f"{d}/not-used.png",
                })

        self.assertFalse(scene.locked)
        self.assertIsNone(scene.image_artifact)


    def test_generation_does_not_delete_unowned_provider_path(self):
        engine = ProductionEngine()
        runtime = Runtime()
        project = runtime.add(engine.create_series("S", [(f"B{i}", "") for i in range(1, 6)]))
        book = project.series.books[0]
        engine.install_manifest(book, [f"Scene {i}" for i in range(1, 41)])
        engine.start_generation(book)
        scene = book.scenes[0]

        with tempfile.TemporaryDirectory() as d:
            source = __import__("pathlib").Path(d) / "provider-owned.png"
            source.write_bytes(b"provider fixture")

            class ExternalPathGenerator:
                def generate(self, payload):
                    return str(source)

            production = ProductionWorker(
                runtime,
                ExternalPathGenerator(),
                MockVisualReviewer(),
                LocalArtifactStore(f"{d}/artifacts"),
            )
            production.generate({
                "project_id": project.id,
                "book_position": book.position,
                "scene_number": scene.number,
                "title": scene.title,
                "locked_brief": book.locked_brief,
            })

            self.assertTrue(source.exists())


if __name__=="__main__":
    unittest.main()
