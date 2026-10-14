import json
from dataclasses import asdict

from backend.domain.models import Book, Scene, Series
from backend.domain.project import PublishingProject
from backend.domain.states import BookState, QAResult, SceneState


def project_to_json(project: PublishingProject) -> str:
    return json.dumps(asdict(project),ensure_ascii=False,indent=2,default=str)


def project_from_json(payload: str) -> PublishingProject:
    data=json.loads(payload)
    books=[]
    for b in data["series"]["books"]:
        scenes=[
            Scene(
                number=s["number"],title=s["title"],state=SceneState(s["state"]),
                generations=s["generations"],
                qa_result=QAResult(s["qa_result"]) if s["qa_result"] else None,
                material_defect=s["material_defect"],
                image_artifact=s.get("image_artifact"),
            )
            for s in b["scenes"]
        ]
        books.append(Book(
            title=b["title"],subtitle=b["subtitle"],position=b["position"],
            locked_brief=b.get("locked_brief", ""),scenes=scenes,
            state=BookState(b["state"]),
        ))
    return PublishingProject(
        Series(data["series"]["name"],books),id=data["id"],
        created_at=data["created_at"],updated_at=data["updated_at"],
    )
