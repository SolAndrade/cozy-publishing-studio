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


if __name__=="__main__":
    unittest.main()
