from hashlib import sha256
from pathlib import Path


class S3ArtifactStore:
    """Private durable artifact storage for S3-compatible object stores."""

    def __init__(
        self,
        bucket: str,
        *,
        endpoint_url: str | None = None,
        region_name: str | None = None,
        client=None,
    ):
        if not bucket:
            raise ValueError("bucket is required")
        self.bucket = bucket
        if client is not None:
            self.client = client
            return
        try:
            import boto3
        except ImportError as exc:
            raise RuntimeError("S3 artifact storage requires boto3") from exc
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint_url or None,
            region_name=region_name or None,
        )

    def put(self, local_path: str, key: str) -> dict:
        source = Path(local_path)
        digest = sha256(source.read_bytes()).hexdigest()
        self.client.upload_file(
            str(source),
            self.bucket,
            key,
            ExtraArgs={"Metadata": {"sha256": digest}},
        )
        return {
            "key": key,
            "bucket": self.bucket,
            "sha256": digest,
        }

    def verify(self, record: dict) -> bool:
        if record.get("bucket") != self.bucket:
            return False
        response = self.client.head_object(Bucket=self.bucket, Key=record["key"])
        metadata = response.get("Metadata", {})
        return metadata.get("sha256") == record.get("sha256")

    def materialize(self, record: dict, destination: str) -> str:
        if record.get("bucket") != self.bucket:
            raise RuntimeError("artifact_bucket_mismatch")
        target=Path(destination)
        target.parent.mkdir(parents=True,exist_ok=True)
        self.client.download_file(self.bucket, record["key"], str(target))
        if sha256(target.read_bytes()).hexdigest() != record.get("sha256"):
            target.unlink(missing_ok=True)
            raise RuntimeError("artifact_integrity_check_failed")
        return str(target)
