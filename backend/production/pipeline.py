from dataclasses import dataclass

from backend.domain.errors import LockedAssetError
from backend.domain.models import Scene
from backend.domain.states import QAResult
from backend.jobs.models import Job, JobType


@dataclass(slots=True)
class ScenePipeline:
    """Plans scene work without ever mutating locked art."""

    def jobs_for(self, project_id: str, book_position: int, scene: Scene) -> list[Job]:
        if scene.locked:
            return []
        base = {
            "project_id": project_id,
            "book_position": book_position,
            "scene_number": scene.number,
        }
        return [
            Job(JobType.GENERATE_SCENE, base | {"title": scene.title}),
            Job(JobType.REVIEW_SCENE, base),
        ]

    def apply_review(self, scene: Scene, result: QAResult, reason: str = "") -> Job | None:
        if scene.locked:
            raise LockedAssetError(f"Scene {scene.number} is already locked")
        scene.qa(result)
        if result == QAResult.PASS:
            return None
        if result == QAResult.FIX_LOCAL:
            return Job(JobType.GENERATE_SCENE, {
                "scene_number": scene.number,
                "mode": "FIX_LOCAL",
                "reason": reason,
            })
        return Job(JobType.GENERATE_SCENE, {
            "scene_number": scene.number,
            "mode": "REGENERATE",
            "reason": reason,
        })
