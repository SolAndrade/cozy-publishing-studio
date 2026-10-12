from dataclasses import dataclass

from backend.domain.models import Book
from backend.domain.states import BookState
from backend.jobs.models import Job, JobType
from backend.jobs.queue import InMemoryJobQueue


@dataclass(slots=True)
class ProductionController:
    queue: InMemoryJobQueue

    def enqueue_next_scene(self, project_id: str, book: Book) -> Job | None:
        if book.state != BookState.GENERATING:
            raise ValueError("Book must be GENERATING")
        scene = next((s for s in book.scenes if not s.locked), None)
        if scene is None:
            book.advance(BookState.ART_LOCKED)
            return None
        job = Job(JobType.GENERATE_SCENE, {
            "project_id": project_id,
            "book_position": book.position,
            "scene_number": scene.number,
            "title": scene.title,
        })
        return self.queue.enqueue(job)

    @staticmethod
    def progress(book: Book) -> dict:
        total = len(book.scenes) or 40
        locked = sum(scene.locked for scene in book.scenes)
        return {
            "locked": locked,
            "total": total,
            "percent": round(locked / total * 100, 1),
            "state": book.state,
            "next_scene": next((s.number for s in book.scenes if not s.locked), None),
        }
