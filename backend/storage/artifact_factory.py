import os

from backend.storage.artifact_store import LocalArtifactStore


class ArtifactStoreNotConfigured(RuntimeError):
    pass


def artifact_store_from_env():
    """Select artifact storage without silently using ephemeral disk in production."""
    env = os.getenv("COZY_ENV", "development").strip().lower()
    provider = os.getenv("COZY_ARTIFACT_STORE", "local").strip().lower()

    if provider == "local":
        if env == "production":
            raise ArtifactStoreNotConfigured(
                "Production requires durable shared artifact storage; local disk is not allowed"
            )
        return LocalArtifactStore(
            os.getenv("COZY_ARTIFACTS_DIR", ".cozy-data/artifacts")
        )

    raise ArtifactStoreNotConfigured(
        f"Artifact store provider {provider!r} is not implemented"
    )
