from backend.domain.models import Book
from backend.domain.states import BookState
from backend.jobs.models import Job,JobType


def recovery_job(project_id: str,book: Book):
    if book.state!=BookState.GENERATING:
        return None
    scene=next((s for s in book.scenes if not s.locked),None)
    if scene is None:
        return None
    job_type=JobType.REVIEW_SCENE if scene.state.value=="GENERATED" else JobType.GENERATE_SCENE
    return Job(job_type,{
        "project_id":project_id,
        "book_position":book.position,
        "scene_number":scene.number,
        "title":scene.title,
        "recovered":True,
    })
