from hashlib import sha256
from pathlib import Path
from shutil import copy2


class LocalArtifactStore:
    """Private-backend artifact storage with content hashes."""

    def __init__(self, root=".cozy-data/artifacts"):
        self.root=Path(root); self.root.mkdir(parents=True,exist_ok=True)

    def put(self, local_path: str, key: str):
        source=Path(local_path)
        target=self.root/key
        target.parent.mkdir(parents=True,exist_ok=True)
        copy2(source,target)
        return {"key":key,"path":str(target),"sha256":sha256(target.read_bytes()).hexdigest()}

    def verify(self, record: dict):
        path=Path(record["path"])
        return path.exists() and sha256(path.read_bytes()).hexdigest()==record["sha256"]
