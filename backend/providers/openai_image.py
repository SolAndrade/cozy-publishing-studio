import base64
import os
from pathlib import Path
from tempfile import mkstemp

from backend.providers.image_contract import GenerationRequest, build_coloring_prompt


class OpenAIImageGenerator:
    """Real image generation via OpenAI Images API; client can be injected for tests."""

    def __init__(self, *, client=None, model=None):
        self.model = model or os.getenv("COZY_OPENAI_IMAGE_MODEL", "gpt-image-2.5-sunburst")
        if client is None:
            from openai import OpenAI
            client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self.client = client

    def generate(self, payload: dict) -> str:
        request = GenerationRequest(
            project_id=payload["project_id"],
            book_position=payload["book_position"],
            scene_number=payload["scene_number"],
            scene_title=payload["title"],
            locked_brief=payload.get("locked_brief", ""),
            mode=payload.get("mode", "GENERATE"),
            defect_reason=payload.get("reason", ""),
        )
        response = self.client.images.generate(
            model=self.model,
            prompt=build_coloring_prompt(request),
        )
        if not response.data or not response.data[0].b64_json:
            raise RuntimeError("image_provider_returned_no_image")
        data = base64.b64decode(response.data[0].b64_json, validate=True)
        if not data.startswith(b"\\x89PNG\\r\\n\\x1a\\n"):
            raise RuntimeError("image_provider_returned_invalid_png")
        fd, path = mkstemp(prefix="cozy-scene-", suffix=".png")
        try:
            with os.fdopen(fd, "wb") as file:
                file.write(data)
        except BaseException:
            Path(path).unlink(missing_ok=True)
            raise
        return path
