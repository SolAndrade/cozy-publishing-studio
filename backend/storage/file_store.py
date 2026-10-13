from pathlib import Path
from threading import Lock

from backend.domain.project import PublishingProject
from backend.storage.codec import project_from_json, project_to_json


class FileProjectStore:
    """Durable JSON persistence for a single backend instance."""

    def __init__(self, root=".cozy-data/projects"):
        self.root=Path(root); self.root.mkdir(parents=True,exist_ok=True); self._lock=Lock()

    def save(self, project: PublishingProject):
        target=self.root/f"{project.id}.json"; temp=target.with_suffix(".tmp")
        with self._lock:
            temp.write_text(project_to_json(project),encoding="utf-8")
            temp.replace(target)
        return target

    def load(self, project_id: str):
        return project_from_json((self.root/f"{project_id}.json").read_text(encoding="utf-8"))

    def list_ids(self):
        return [p.stem for p in self.root.glob("*.json")]
