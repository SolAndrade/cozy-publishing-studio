import base64
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from backend.orchestrator.engine import ProductionEngine
from backend.providers.openai_image import OpenAIImageGenerator
from backend.providers.openai_vision import OpenAIVisualReviewer
from backend.runtime import Runtime
from backend.storage.artifact_store import LocalArtifactStore
from backend.workers.production_worker import ProductionWorker
from backend.workers.runner import Worker


PNG = bytes.fromhex("89504e470d0a1a0a") + b"cozy-test"


class FakeImages:
    def __init__(self):
        self.kwargs = None

    def generate(self, **kwargs):
        self.kwargs = kwargs
        return SimpleNamespace(data=[
            SimpleNamespace(b64_json=base64.b64encode(PNG).decode("ascii"))
        ])


class FakeResponses:
    def __init__(self):
        self.kwargs = None

    def create(self, **kwargs):
        self.kwargs = kwargs
        return SimpleNamespace(output_text=json.dumps({"result": "PASS", "reason": ""}))


class OpenAIPipelineTests(unittest.TestCase):
    def test_generation_storage_and_visual_review_lock_scene(self):
        engine = ProductionEngine()
        runtime = Runtime()
        concepts = [("Book 1", "A cozy coloring book", "Locked European village identity")] + [
            (f"Book {i}", f"Subtitle {i}", f"Visual identity {i}") for i in range(2, 6)
        ]
        project = runtime.add(engine.create_series("Series", concepts))
        book = project.series.books[0]
        engine.install_manifest(book, [f"Scene {i}" for i in range(1, 41)])
        engine.start_generation(book)
        runtime.production.enqueue_next_scene(project.id, book)

        images = FakeImages()
        responses = FakeResponses()
        generator = OpenAIImageGenerator(client=SimpleNamespace(images=images), model="image-test")
        reviewer = OpenAIVisualReviewer(client=SimpleNamespace(responses=responses), model="vision-test")

        with tempfile.TemporaryDirectory() as d:
            worker = Worker(
                runtime.queue,
                ProductionWorker(
                    runtime, generator, reviewer, LocalArtifactStore(f"{d}/artifacts")
                ).handlers(),
            )
            before = set(Path("/tmp").glob("cozy-scene-*.png"))
            generated = worker.run_one()
            after = set(Path("/tmp").glob("cozy-scene-*.png"))
            reviewed = worker.run_one()

            self.assertIsNotNone(generated)
            self.assertIsNotNone(reviewed)
            self.assertTrue(book.scenes[0].locked)
            self.assertIsNotNone(book.scenes[0].image_artifact)
            self.assertIn("Locked European village identity", images.kwargs["prompt"])
            self.assertIn("data:image/png;base64,", str(responses.kwargs["input"]))
            self.assertIn("Book identity: Locked European village identity", str(responses.kwargs["input"]))
            self.assertIn("Scene: Scene 1", str(responses.kwargs["input"]))
            self.assertEqual(after, before)

