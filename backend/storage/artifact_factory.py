import os

from backend.storage.artifact_store import LocalArtifactStore
from backend.storage.s3_artifact_store import S3ArtifactStore


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

    if provider == "s3":
        bucket = os.getenv("COZY_S3_BUCKET", "").strip()
        if not bucket:
            raise ArtifactStoreNotConfigured("COZY_S3_BUCKET is required for S3 artifact storage")
        return S3ArtifactStore(
            bucket,
            endpoint_url=os.getenv("COZY_S3_ENDPOINT", "").strip() or None,
            region_name=os.getenv("COZY_S3_REGION", "").strip() or None,
        )

    raise ArtifactStoreNotConfigured(
        f"Artifact store provider {provider!r} is not implemented"
    )
