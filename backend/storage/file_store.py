import json
from dataclasses import asdict
from pathlib import Path
from threading import Lock

from backend.domain.models import Book, Scene, Series
from backend.domain.project import PublishingProject
from backend.domain.states import BookState, QAResult, SceneState


class FileProjectStore:
    """Durable JSON persistence for a single backend instance."""

    def __init__(self, root=".cozy-data/projects"):
        self.root=Path(root); self.root.mkdir(parents=True,exist_ok=True); self._lock=Lock()

    def save(self, project: PublishingProject):
        target=self.root/f"{project.id}.json"; temp=target.with_suffix(".tmp")
        with self._lock:
            temp.write_text(json.dumps(asdict(project),ensure_ascii=False,indent=2,default=str),encoding="utf-8")
            temp.replace(target)
        return target

    def load(self, project_id: str):
        data=json.loads((self.root/f"{project_id}.json").read_text(encoding="utf-8"))
        books=[]
        for b in data["series"]["books"]:
            scenes=[Scene(number=s["number"],title=s["title"],state=SceneState(s["state"]),generations=s["generations"],qa_result=QAResult(s["qa_result"]) if s["qa_result"] else None,material_defect=s["material_defect"]) for s in b["scenes"]]
            books.append(Book(title=b["title"],subtitle=b["subtitle"],position=b["position"],scenes=scenes,state=BookState(b["state"])))
        return PublishingProject(Series(data["series"]["name"],books),id=data["id"],created_at=data["created_at"],updated_at=data["updated_at"])

    def list_ids(self):
        return [p.stem for p in self.root.glob("*.json")]
