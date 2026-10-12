from dataclasses import dataclass, field
from hashlib import sha256
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Artifact:
    kind: str
    path: str
    sha256: str


@dataclass(slots=True)
class ArtifactManifest:
    artifacts: list[Artifact] = field(default_factory=list)

    def add_file(self, kind: str, path: str) -> Artifact:
        source = Path(path)
        digest = sha256(source.read_bytes()).hexdigest()
        artifact = Artifact(kind, str(source), digest)
        self.artifacts.append(artifact)
        return artifact

    def verify(self, artifact: Artifact) -> bool:
        source = Path(artifact.path)
        return source.exists() and sha256(source.read_bytes()).hexdigest() == artifact.sha256
