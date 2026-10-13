import os

from backend.providers.mock import MockImageGenerator, MockVisualReviewer


class ProviderNotConfigured(RuntimeError):
    pass


class ProviderFactory:
    """Construct only adapters that are actually implemented."""

    @staticmethod
    def text_provider_name() -> str:
        return os.getenv("COZY_TEXT_PROVIDER", "").strip().lower()

    @staticmethod
    def image_provider_name() -> str:
        return os.getenv("COZY_IMAGE_PROVIDER", "mock").strip().lower() or "mock"

    @staticmethod
    def vision_provider_name() -> str:
        return os.getenv("COZY_VISION_PROVIDER", "mock").strip().lower() or "mock"

    @classmethod
    def image_generator(cls):
        name=cls.image_provider_name()
        if name=="mock":
            return MockImageGenerator(os.getenv("COZY_MOCK_IMAGES_DIR",".cozy-data/mock-images"))
        raise ProviderNotConfigured(f"Image provider {name!r} is not implemented")

    @classmethod
    def visual_reviewer(cls):
        name=cls.vision_provider_name()
        if name=="mock":
            return MockVisualReviewer()
        raise ProviderNotConfigured(f"Vision provider {name!r} is not implemented")

    @classmethod
    def readiness(cls) -> dict:
        image=cls.image_provider_name()
        vision=cls.vision_provider_name()
        return {
            "text_planner": bool(cls.text_provider_name()),
            "image_generator": image=="mock",
            "visual_reviewer": vision=="mock",
        }
