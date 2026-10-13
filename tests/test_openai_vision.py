import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from backend.providers.openai_vision import OpenAIVisualReviewer


class FakeResponses:
    def __init__(self, verdict):
        self.verdict = verdict
        self.kwargs = None

    def create(self, **kwargs):
        self.kwargs = kwargs
        return SimpleNamespace(output_text=json.dumps(self.verdict))


class OpenAIVisionTests(unittest.TestCase):
    def test_sends_image_and_validates_pass(self):
        with tempfile.TemporaryDirectory() as d:
            image = Path(d) / "scene.png"
            image.write_bytes(bytes.fromhex("89504e470d0a1a0a") + b"test")
            responses = FakeResponses({"result": "PASS", "reason": ""})
            reviewer = OpenAIVisualReviewer(client=SimpleNamespace(responses=responses), model="test-model")
            verdict = reviewer.review(str(image), "Cozy cafe")
            self.assertEqual(verdict["result"], "PASS")
            self.assertEqual(responses.kwargs["model"], "test-model")
            self.assertIn("data:image/png;base64,", str(responses.kwargs["input"]))

    def test_rejects_vague_failure(self):
        with tempfile.TemporaryDirectory() as d:
            image = Path(d) / "scene.png"
            image.write_bytes(bytes.fromhex("89504e470d0a1a0a") + b"test")
            responses = FakeResponses({"result": "REGENERATE", "reason": ""})
            reviewer = OpenAIVisualReviewer(client=SimpleNamespace(responses=responses))
            with self.assertRaisesRegex(ValueError, "reason"):
                reviewer.review(str(image), "Cozy cafe")


if __name__ == "__main__":
    unittest.main()
