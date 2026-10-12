import tempfile
import unittest
from pathlib import Path

from backend.artifacts.manifest import ArtifactManifest


class ArtifactTests(unittest.TestCase):
    def test_hash_detects_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "master.txt"
            path.write_text("locked", encoding="utf-8")
            manifest = ArtifactManifest()
            artifact = manifest.add_file("MASTER", str(path))
            self.assertTrue(manifest.verify(artifact))
            path.write_text("changed", encoding="utf-8")
            self.assertFalse(manifest.verify(artifact))


if __name__ == "__main__":
    unittest.main()
