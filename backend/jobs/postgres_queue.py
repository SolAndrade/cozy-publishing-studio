import json
from dataclasses import asdict
from uuid import uuid4

from backend.jobs.models import Job, JobStatus, JobType


class PostgresJobQueue:
    """Shared PostgreSQL queue with atomic worker claims."""

    def __init__(self, database_url: str):
        if not database_url:
            raise ValueError("database_url is required")
        self.database_url=database_url
        self._ensure_schema()

    def _connect(self):
        try:
            import psycopg
        except ImportError as exc:
            raise RuntimeError("PostgreSQL queue requires the psycopg package") from exc
        return psycopg.connect(self.database_url)

    def _ensure_schema(self):
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cozy_jobs (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    payload JSONB NOT NULL,
                    status TEXT NOT NULL,
                    attempts INTEGER NOT NULL,
                    max_attempts INTEGER NOT NULL,
                    error TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """)
            conn.execute("ALTER TABLE cozy_jobs ADD COLUMN IF NOT EXISTS claim_token TEXT")
            conn.execute(
                "CREATE INDEX IF NOT EXISTS cozy_jobs_status_created_idx ON cozy_jobs(status,created_at)"
            )

    @staticmethod
    def _job(row) -> Job:
        payload=row[2] if isinstance(row[2],dict) else json.loads(row[2])
        return Job(
            type=JobType(row[1]),payload=payload,id=row[0],
            status=JobStatus(row[3]),attempts=row[4],
            max_attempts=row[5],error=row[6],
            claim_token=row[7] if len(row) > 7 else None,
        )

    def enqueue(self, job: Job) -> Job:
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO cozy_jobs
                   (id,type,payload,status,attempts,max_attempts,error)
                   VALUES (%s,%s,%s::jsonb,%s,%s,%s,%s)
                   ON CONFLICT (id) DO NOTHING""",
                (job.id,job.type.value,json.dumps(job.payload),job.status.value,
                 job.attempts,job.max_attempts,job.error),
            )
        return job

    def next(self) -> Job | None:
        claim_token=str(uuid4())
        with self._connect() as conn:
            row=conn.execute(
                """UPDATE cozy_jobs SET status=%s, attempts=attempts+1,
                          error=NULL, claim_token=%s, updated_at=NOW()
                   WHERE id=(
                       SELECT id FROM cozy_jobs
                       WHERE status=%s AND attempts < max_attempts
                       ORDER BY created_at
                       FOR UPDATE SKIP LOCKED LIMIT 1
                   )
                   RETURNING id,type,payload,status,attempts,max_attempts,error,claim_token""",
                (JobStatus.RUNNING.value,claim_token,JobStatus.QUEUED.value),
            ).fetchone()
        return self._job(row) if row else None

    def recover_stale_running(self, stale_after_seconds: int = 900) -> tuple[int, int]:
        """Fence abandoned claims, requeue retryable jobs, and block exhausted jobs."""
        if stale_after_seconds < 1:
            raise ValueError("stale_after_seconds must be positive")
        with self._connect() as conn:
            retryable=conn.execute(
                """UPDATE cozy_jobs
                   SET status=%s,
                       error='recovered_after_stale_claim',
                       claim_token=NULL,
                       updated_at=NOW()
                   WHERE status=%s
                     AND attempts < max_attempts
                     AND updated_at < NOW() - (%s * INTERVAL '1 second')""",
                (JobStatus.QUEUED.value,JobStatus.RUNNING.value,stale_after_seconds),
            ).rowcount
            exhausted=conn.execute(
                """UPDATE cozy_jobs
                   SET status=%s,
                       error='stale_running_job_retry_limit_reached',
                       claim_token=NULL,
                       updated_at=NOW()
                   WHERE status=%s
                     AND attempts >= max_attempts
                     AND updated_at < NOW() - (%s * INTERVAL '1 second')""",
                (JobStatus.BLOCKED.value,JobStatus.RUNNING.value,stale_after_seconds),
            ).rowcount
        return retryable, exhausted

    def block_stale_running(self, stale_after_seconds: int = 900) -> int:
        """Fail closed on abandoned RUNNING jobs instead of risking duplicate work."""
        if stale_after_seconds < 1:
            raise ValueError("stale_after_seconds must be positive")
        with self._connect() as conn:
            result=conn.execute(
                """UPDATE cozy_jobs
                   SET status=%s,
                       error='stale_running_job_requires_review',
                       claim_token=NULL,
                       updated_at=NOW()
                   WHERE status=%s
                     AND updated_at < NOW() - (%s * INTERVAL '1 second')""",
                (JobStatus.BLOCKED.value,JobStatus.RUNNING.value,stale_after_seconds),
            )
            return result.rowcount

    def save(self, job: Job) -> None:
        with self._connect() as conn:
            if job.claim_token:
                result=conn.execute(
                    """UPDATE cozy_jobs SET status=%s, attempts=%s, error=%s,
                              payload=%s::jsonb, updated_at=NOW()
                       WHERE id=%s AND claim_token=%s""",
                    (job.status.value,job.attempts,job.error,json.dumps(job.payload),
                     job.id,job.claim_token),
                )
                if result.rowcount != 1:
                    raise RuntimeError("job_claim_lost")
            else:
                conn.execute(
                    """UPDATE cozy_jobs SET status=%s, attempts=%s, error=%s,
                              payload=%s::jsonb, updated_at=NOW()
                       WHERE id=%s AND claim_token IS NULL""",
                    (job.status.value,job.attempts,job.error,json.dumps(job.payload),job.id),
                )

    def __len__(self) -> int:
        with self._connect() as conn:
            row=conn.execute(
                "SELECT COUNT(*) FROM cozy_jobs WHERE status=%s",(JobStatus.QUEUED.value,)
            ).fetchone()
        return row[0]
