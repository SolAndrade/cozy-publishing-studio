from collections import deque

from .models import Job, JobStatus


class InMemoryJobQueue:
    """Development queue. A durable cloud queue will implement the same interface."""

    def __init__(self) -> None:
        self._items: deque[Job] = deque()

    def enqueue(self, job: Job) -> Job:
        self._items.append(job)
        return job

    def next(self) -> Job | None:
        while self._items:
            job = self._items.popleft()
            if job.status == JobStatus.QUEUED:
                return job
        return None

    def __len__(self) -> int:
        return len(self._items)
