from dataclasses import dataclass

from backend.domain.states import QAResult
from backend.jobs.models import Job, JobType
from backend.runtime import Runtime


@dataclass(slots=True)
class ProductionWorker:
    runtime: Runtime
    image_generator: object
    visual_reviewer: object

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
        self.runtime.queue.enqueue(Job(JobType.REVIEW_SCENE,{
            "project_id":project.id,"book_position":book.position,
            "scene_number":scene.number,"image_path":path,
        }))

    def review(self, payload):
        project,book,scene=self._scene(payload)
        if scene.locked:
            return
        verdict=self.visual_reviewer.review(payload["image_path"], scene.title)
        result=QAResult(verdict["result"])
        reason=verdict.get("reason","")
        scene.qa(result)
        self.runtime.persist(project)
        if result==QAResult.PASS:
            self.runtime.production.enqueue_next_scene(project.id,book)
            return
        if result==QAResult.REGENERATE:
            scene.record_material_defect(reason or "material visual defect")
            self.runtime.persist(project)
        self.runtime.queue.enqueue(Job(JobType.GENERATE_SCENE,{
            "project_id":project.id,"book_position":book.position,
            "scene_number":scene.number,"title":scene.title,
            "mode":result.value,"reason":reason,
        }))

    def handlers(self):
        return {JobType.GENERATE_SCENE:self.generate,JobType.REVIEW_SCENE:self.review}
