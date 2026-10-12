from typing import Protocol


class TextPlanner(Protocol):
    def propose_series(self, theme: str) -> dict: ...
    def build_manifest(self, book_title: str, brief: str) -> list[str]: ...


class ImageGenerator(Protocol):
    def generate(self, prompt: str, output_path: str) -> str: ...


class VisualReviewer(Protocol):
    def review(self, image_path: str, brief: str) -> dict: ...


class ArtifactStore(Protocol):
    def put(self, local_path: str, key: str) -> str: ...
