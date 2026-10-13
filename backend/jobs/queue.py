import json
from collections import deque
from dataclasses import asdict
from pathlib import Path
from threading import Lock

from .models import Job, JobStatus, JobType


class InMemoryJobQueue:
    """Development queue with the same interface as the durable file queue."""

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

    def save(self, job: Job) -> None:
        return None

    def __len__(self) -> int:
        return len(self._items)


class FileJobQueue:
    """Small durable FIFO queue for a single backend/worker instance."""

    def __init__(self, root: str | Path = ".cozy-data/jobs") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()

    def _path(self, job_id: str) -> Path:
        return self.root / f"{job_id}.json"

    def _write(self, job: Job) -> None:
        target = self._path(job.id)
        temp = target.with_suffix(".tmp")
        payload = asdict(job)
        payload["type"] = job.type.value
        payload["status"] = job.status.value
        temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        temp.replace(target)

    def enqueue(self, job: Job) -> Job:
        with self._lock:
            self._write(job)
        return job

    def save(self, job: Job) -> None:
        with self._lock:
            self._write(job)

    def _load(self, path: Path) -> Job:
        data = json.loads(path.read_text(encoding="utf-8"))
        return Job(
            type=JobType(data["type"]),
            payload=data["payload"],
            id=data["id"],
            status=JobStatus(data["status"]),
            attempts=data["attempts"],
            max_attempts=data["max_attempts"],
            error=data["error"],
            claim_token=data.get("claim_token"),
        )

    def next(self) -> Job | None:
        with self._lock:
            candidates = []
            for path in self.root.glob("*.json"):
                job = self._load(path)
                if job.status == JobStatus.QUEUED:
                    candidates.append((path.stat().st_mtime_ns, job.id, job))
            if not candidates:
                return None
            _, _, job = min(candidates)
            return job

    def __len__(self) -> int:
        return sum(1 for path in self.root.glob("*.json") if self._load(path).status == JobStatus.QUEUED)
