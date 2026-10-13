import os
import tempfile
import unittest
from unittest.mock import patch

from backend.storage.artifact_factory import (
    ArtifactStoreNotConfigured,
    artifact_store_from_env,
)
from backend.storage.artifact_store import LocalArtifactStore


class ArtifactFactoryTests(unittest.TestCase):
    def test_development_can_use_local_artifacts(self):
        with tempfile.TemporaryDirectory() as d:
            with patch.dict(
                os.environ,
                {
                    "COZY_ENV": "development",
                    "COZY_ARTIFACT_STORE": "local",
                    "COZY_ARTIFACTS_DIR": d,
                },
                clear=True,
            ):
                store = artifact_store_from_env()
        self.assertIsInstance(store, LocalArtifactStore)

    def test_production_rejects_local_artifacts(self):
        with patch.dict(
            os.environ,
            {"COZY_ENV": "production", "COZY_ARTIFACT_STORE": "local"},
            clear=True,
        ):
            with self.assertRaisesRegex(
                ArtifactStoreNotConfigured, "durable shared artifact storage"
            ):
                artifact_store_from_env()

    def test_unknown_provider_fails_explicitly(self):
        with patch.dict(
            os.environ,
            {"COZY_ENV": "production", "COZY_ARTIFACT_STORE": "not-real"},
            clear=True,
        ):
            with self.assertRaisesRegex(ArtifactStoreNotConfigured, "not implemented"):
                artifact_store_from_env()


if __name__ == "__main__":
    unittest.main()
