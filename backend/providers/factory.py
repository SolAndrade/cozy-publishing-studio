import os


class ProviderNotConfigured(RuntimeError):
    pass


class ProviderFactory:
    """Central place for private server-side provider selection."""

    @staticmethod
    def text_provider_name() -> str:
        return os.getenv("COZY_TEXT_PROVIDER", "").strip()

    @staticmethod
    def image_provider_name() -> str:
        return os.getenv("COZY_IMAGE_PROVIDER", "").strip()

    @classmethod
    def readiness(cls) -> dict:
        return {
            "text_planner": bool(cls.text_provider_name()),
            "image_generator": bool(cls.image_provider_name()),
            "storage": bool(os.getenv("COZY_STORAGE_PROVIDER", "").strip()),
        }
