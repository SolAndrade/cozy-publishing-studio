import base64
import json
import os
from pathlib import Path

from backend.providers.review_contract import normalize_review


class OpenAIVisualReviewer:
    """Visual QA with an actual image input and validated structured verdict."""

    def __init__(self, *, client=None, model=None):
        self.model = model or os.getenv("COZY_OPENAI_VISION_MODEL", "gpt-5.4-mini")
        if client is None:
            from openai import OpenAI
            client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self.client = client

    def review(self, image_path: str, brief: str) -> dict:
        image = Path(image_path).read_bytes()
        if not image.startswith(bytes.fromhex("89504e470d0a1a0a")):
            raise ValueError("review_requires_png_image")
        encoded = base64.b64encode(image).decode("ascii")
        response = self.client.responses.create(
            model=self.model,
            input=[{
                "role": "user",
                "content": [
                    {"type": "input_text", "text": (
                        "Review this adult coloring-book line-art image against the scene brief: "
                        + brief
                        + ". Check pure white background, black clean lines, no gray shading, "
                        "no logos/readable text, structural plausibility, and colorable spaces. "
                        "Return PASS only if material constraints are satisfied; otherwise "
                        "FIX_LOCAL or REGENERATE with a specific reason."
                    )},
                    {"type": "input_image", "image_url": "data:image/png;base64," + encoded},
                ],
            }],
            text={"format": {
                "type": "json_schema",
                "name": "cozy_visual_review",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "result": {"type": "string", "enum": ["PASS", "FIX_LOCAL", "REGENERATE"]},
                        "reason": {"type": "string"},
                    },
                    "required": ["result", "reason"],
                    "additionalProperties": False,
                },
            }},
        )
        if not response.output_text:
            raise RuntimeError("vision_provider_returned_no_review")
        return normalize_review(json.loads(response.output_text))
