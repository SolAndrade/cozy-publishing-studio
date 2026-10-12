from collections.abc import Callable

from backend.jobs.models import Job, JobStatus, JobType
from backend.jobs.queue import InMemoryJobQueue


Handler = Callable[[dict], None]


class Worker:
    def __init__(self, queue: InMemoryJobQueue, handlers: dict[JobType, Handler]) -> None:
        self.queue = queue
        self.handlers = handlers

    def run_one(self) -> Job | None:
        job = self.queue.next()
        if job is None:
            return None
        try:
            job.start()
            handler = self.handlers.get(job.type)
            if handler is None:
                raise RuntimeError(f"No handler registered for {job.type}")
            handler(job.payload)
            job.succeed()
        except Exception as exc:
            if job.status == JobStatus.RUNNING:
                job.fail(str(exc))
        return job
