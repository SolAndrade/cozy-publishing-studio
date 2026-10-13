import base64
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from backend.providers.openai_image import OpenAIImageGenerator


class FakeImages:
    def __init__(self, image):
        self.image = image
        self.kwargs = None

    def generate(self, **kwargs):
        self.kwargs = kwargs
        return SimpleNamespace(data=[SimpleNamespace(b64_json=base64.b64encode(self.image).decode())])


class OpenAIImageTests(unittest.TestCase):
    def test_generates_png_and_preserves_locked_prompt(self):
        images = FakeImages(bytes.fromhex("89504e470d0a1a0a") + b"test")
        generator = OpenAIImageGenerator(client=SimpleNamespace(images=images), model="test-model")
        path = generator.generate({
            "project_id": "p", "book_position": 1, "scene_number": 2,
            "title": "Cozy cafe", "locked_brief": "European village",
        })
        try:
            self.assertTrue(Path(path).read_bytes().startswith(bytes.fromhex("89504e470d0a1a0a")))
            self.assertIn("European village", images.kwargs["prompt"])
            self.assertEqual(images.kwargs["model"], "test-model")
        finally:
            Path(path).unlink(missing_ok=True)

    def test_rejects_non_png_response(self):
        images = FakeImages(b"not an image")
        generator = OpenAIImageGenerator(client=SimpleNamespace(images=images))
        with self.assertRaisesRegex(RuntimeError, "invalid_png"):
            generator.generate({
                "project_id": "p", "book_position": 1, "scene_number": 1,
                "title": "Room",
            })


if __name__ == "__main__":
    unittest.main()
