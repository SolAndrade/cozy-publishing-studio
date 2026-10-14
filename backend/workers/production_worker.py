from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

from backend.domain.states import QAResult
from backend.jobs.models import Job, JobType
from backend.runtime import Runtime


@dataclass(slots=True)
class ProductionWorker:
    runtime: Runtime
    image_generator: object
    visual_reviewer: object
    artifact_store: object | None = None

    def _scene(self, payload):
        project=self.runtime.get(payload["project_id"])
        book=next(b for b in project.series.books if b.position==payload["book_position"])
        scene=next(s for s in book.scenes if s.number==payload["scene_number"])
        return project,book,scene

    def generate(self, payload):
        project,book,scene=self._scene(payload)
        if scene.locked:
            return
        path=self.image_generator.generate(payload)
        scene.record_generation()
        self.runtime.persist(project)
        review_payload={
            "project_id":project.id,"book_position":book.position,
            "scene_number":scene.number,
        }
        if self.artifact_store is None:
            review_payload["image_path"]=path
        else:
            suffix=Path(path).suffix or ".png"
            key=(f"projects/{project.id}/books/{book.position}/scenes/{scene.number}/"
                 f"generation-{scene.generations}-{uuid4().hex}{suffix}")
            try:
                review_payload["image_artifact"]=self.artifact_store.put(path,key)
            finally:
                Path(path).unlink(missing_ok=True)
        self.runtime.queue.enqueue(Job(JobType.REVIEW_SCENE,review_payload))

    def review(self, payload):
        project,book,scene=self._scene(payload)
        if scene.locked:
            return
        if "image_artifact" in payload:
            if self.artifact_store is None:
                raise RuntimeError("artifact_store_required_for_review")
            with TemporaryDirectory() as temp_dir:
                destination=str(Path(temp_dir)/"scene-image")
                image_path=self.artifact_store.materialize(payload["image_artifact"],destination)
                verdict=self.visual_reviewer.review(image_path, scene.title)
        else:
            verdict=self.visual_reviewer.review(payload["image_path"], scene.title)
        result=QAResult(verdict["result"])
        reason=verdict.get("reason","")
        scene.qa(result)
        self.runtime.persist(project)
        if result==QAResult.PASS:
            if self.artifact_store is not None:
                artifact=payload.get("image_artifact")
                if not artifact:
                    raise RuntimeError("approved_scene_requires_durable_artifact")
                scene.image_artifact=artifact
                self.runtime.persist(project)
            self.runtime.production.enqueue_next_scene(project.id,book)
            return
        if result==QAResult.REGENERATE:
            scene.record_material_defect(reason or "material visual defect")
            self.runtime.persist(project)
        self.runtime.queue.enqueue(Job(JobType.GENERATE_SCENE,{
            "project_id":project.id,"book_position":book.position,
            "scene_number":scene.number,"title":scene.title,
            "locked_brief":book.locked_brief,
            "mode":result.value,"reason":reason,
        }))

    def handlers(self):
        return {JobType.GENERATE_SCENE:self.generate,JobType.REVIEW_SCENE:self.review}
