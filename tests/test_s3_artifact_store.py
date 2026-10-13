import tempfile
import unittest
from pathlib import Path

from backend.storage.s3_artifact_store import S3ArtifactStore


class FakeS3Client:
    def __init__(self):
        self.objects = {}

    def upload_file(self, filename, bucket, key, ExtraArgs=None):
        self.objects[(bucket, key)] = {
            "body": Path(filename).read_bytes(),
            "Metadata": (ExtraArgs or {}).get("Metadata", {}),
        }

    def head_object(self, *, Bucket, Key):
        return {"Metadata": self.objects[(Bucket, Key)]["Metadata"]}

    def download_file(self, bucket, key, filename):
        Path(filename).write_bytes(self.objects[(bucket, key)]["body"])


class S3ArtifactStoreTests(unittest.TestCase):
    def test_put_records_hash_and_verify_checks_remote_metadata(self):
        client = FakeS3Client()
        store = S3ArtifactStore("private-books", client=client)
        with tempfile.TemporaryDirectory() as d:
            source = Path(d) / "interior.pdf"
            source.write_bytes(b"private-pdf")
            record = store.put(str(source), "projects/p1/interior.pdf")

        self.assertEqual(record["bucket"], "private-books")
        self.assertTrue(record["sha256"])
        self.assertTrue(store.verify(record))

        client.objects[("private-books", "projects/p1/interior.pdf")]["Metadata"]["sha256"] = "wrong"
        self.assertFalse(store.verify(record))

    def test_materialize_downloads_and_verifies_content(self):
        client = FakeS3Client()
        store = S3ArtifactStore("private-books", client=client)
        with tempfile.TemporaryDirectory() as d:
            source = Path(d) / "scene.png"
            source.write_bytes(b"scene-bytes")
            record = store.put(str(source), "projects/p1/scene.png")
            destination = Path(d) / "review" / "scene.png"
            path = store.materialize(record, str(destination))
            self.assertEqual(Path(path).read_bytes(), b"scene-bytes")

    def test_materialize_rejects_tampered_remote_content(self):
        client = FakeS3Client()
        store = S3ArtifactStore("private-books", client=client)
        with tempfile.TemporaryDirectory() as d:
            source = Path(d) / "scene.png"
            source.write_bytes(b"original")
            record = store.put(str(source), "projects/p1/scene.png")
            client.objects[("private-books", "projects/p1/scene.png")]["body"] = b"tampered"
            destination = Path(d) / "download.png"
            with self.assertRaisesRegex(RuntimeError, "integrity"):
                store.materialize(record, str(destination))
            self.assertFalse(destination.exists())

    def test_bucket_is_required(self):
        with self.assertRaisesRegex(ValueError, "bucket"):
            S3ArtifactStore("", client=FakeS3Client())


if __name__ == "__main__":
    unittest.main()
