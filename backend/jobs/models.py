from dataclasses import dataclass, field
from enum import StrEnum
from uuid import uuid4


class JobStatus(StrEnum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"


class JobType(StrEnum):
    PLAN_BOOK = "PLAN_BOOK"
    GENERATE_SCENE = "GENERATE_SCENE"
    REVIEW_SCENE = "REVIEW_SCENE"
    BUILD_INTERIOR = "BUILD_INTERIOR"
    BUILD_COVER = "BUILD_COVER"
    BUILD_METADATA = "BUILD_METADATA"
    PREPARE_KDP_DRAFT = "PREPARE_KDP_DRAFT"


@dataclass(slots=True)
class Job:
    type: JobType
    payload: dict
    id: str = field(default_factory=lambda: str(uuid4()))
    status: JobStatus = JobStatus.QUEUED
    attempts: int = 0
    max_attempts: int = 3
    error: str | None = None

    def start(self) -> None:
        if self.status not in {JobStatus.QUEUED, JobStatus.FAILED}:
            raise ValueError(f"Cannot start job from {self.status}")
        if self.attempts >= self.max_attempts:
            self.status = JobStatus.BLOCKED
            raise ValueError("Job retry limit reached")
        self.attempts += 1
        self.status = JobStatus.RUNNING
        self.error = None

    def succeed(self) -> None:
        if self.status != JobStatus.RUNNING:
            raise ValueError("Only RUNNING jobs can succeed")
        self.status = JobStatus.SUCCEEDED

    def fail(self, error: str) -> None:
        if self.status != JobStatus.RUNNING:
            raise ValueError("Only RUNNING jobs can fail")
        self.status = JobStatus.FAILED
        self.error = error
