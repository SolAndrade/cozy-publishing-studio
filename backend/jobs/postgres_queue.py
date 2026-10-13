import json
from dataclasses import asdict

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
        with self._connect() as conn:
            row=conn.execute(
                """UPDATE cozy_jobs SET status=%s, attempts=attempts+1,
                          error=NULL, updated_at=NOW()
                   WHERE id=(
                       SELECT id FROM cozy_jobs
                       WHERE status=%s AND attempts < max_attempts
                       ORDER BY created_at
                       FOR UPDATE SKIP LOCKED LIMIT 1
                   )
                   RETURNING id,type,payload,status,attempts,max_attempts,error""",
                (JobStatus.RUNNING.value,JobStatus.QUEUED.value),
            ).fetchone()
        return self._job(row) if row else None

    def save(self, job: Job) -> None:
        with self._connect() as conn:
            conn.execute(
                """UPDATE cozy_jobs SET status=%s, attempts=%s, error=%s,
                          payload=%s::jsonb, updated_at=NOW() WHERE id=%s""",
                (job.status.value,job.attempts,job.error,json.dumps(job.payload),job.id),
            )

    def __len__(self) -> int:
        with self._connect() as conn:
            row=conn.execute(
                "SELECT COUNT(*) FROM cozy_jobs WHERE status=%s",(JobStatus.QUEUED.value,)
            ).fetchone()
        return row[0]
