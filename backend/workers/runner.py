from collections.abc import Callable

from backend.jobs.errors import RetryableJobError\nfrom backend.jobs.models import Job, JobStatus, JobType


Handler = Callable[[dict], None]


class Worker:
    def __init__(self, queue, handlers: dict[JobType, Handler]) -> None:
        self.queue = queue
        self.handlers = handlers

    def run_one(self) -> Job | None:
        job = self.queue.next()
        if job is None:
            return None
        try:
            if job.status != JobStatus.RUNNING:
                job.start()
                self.queue.save(job)
            handler = self.handlers.get(job.type)
            if handler is None:
                raise RuntimeError(f"No handler registered for {job.type}")
            handler(job.payload)
            job.succeed()
        except Exception as exc:
            if job.status == JobStatus.RUNNING:
                job.fail(str(exc))
        self.queue.save(job)
        return job
