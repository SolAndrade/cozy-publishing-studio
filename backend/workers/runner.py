from collections.abc import Callable

from backend.jobs.errors import RetryableJobError
from backend.jobs.models import Job, JobStatus, JobType


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
        except RetryableJobError as exc:
            if job.status == JobStatus.RUNNING:
                job.error = str(exc)
                job.status = (
                    JobStatus.QUEUED
                    if job.attempts < job.max_attempts
                    else JobStatus.BLOCKED
                )
                if job.status == JobStatus.QUEUED:
                    requeue = getattr(self.queue, "requeue_claimed", None)
                    if requeue is None:
                        job.claim_token = None
                        self.queue.enqueue(job)
                    else:
                        requeue(job)
        except Exception as exc:
            if job.status == JobStatus.RUNNING:
                job.fail(str(exc))
        self.queue.save(job)
        return job
