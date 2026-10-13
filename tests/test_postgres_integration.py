import os
import unittest
from uuid import uuid4

from backend.domain.models import Book, Series
from backend.domain.project import PublishingProject
from backend.jobs.models import Job, JobStatus, JobType
from backend.jobs.postgres_queue import PostgresJobQueue
from backend.storage.postgres import PostgresProjectStore


@unittest.skipUnless(os.getenv("COZY_TEST_DATABASE_URL"), "PostgreSQL test database not configured")
class PostgresIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.database_url = os.environ["COZY_TEST_DATABASE_URL"]

    def setUp(self):
        import psycopg
        with psycopg.connect(self.database_url) as conn:
            conn.execute("DROP TABLE IF EXISTS cozy_jobs")
            conn.execute("DROP TABLE IF EXISTS cozy_projects")

    def test_project_round_trip(self):
        store = PostgresProjectStore(self.database_url)
        project = PublishingProject(
            Series(
                "Integration Series",
                [Book(f"Book {i}", "Subtitle", i) for i in range(1, 6)],
            )
        )
        store.save(project)

        loaded = store.load(project.id)

        self.assertEqual(loaded.id, project.id)
        self.assertEqual(loaded.series.name, "Integration Series")
        self.assertEqual(loaded.series.books[0].title, "Book 1")

    def test_stale_running_job_is_blocked_without_requeue(self):
        import psycopg
        queue = PostgresJobQueue(self.database_url)
        job = Job(JobType.PLAN_BOOK, {"project_id": str(uuid4())})
        queue.enqueue(job)
        claimed = queue.next()
        self.assertEqual(claimed.status, JobStatus.RUNNING)

        with psycopg.connect(self.database_url) as conn:
            conn.execute(
                "UPDATE cozy_jobs SET updated_at=NOW() - INTERVAL '1 hour' WHERE id=%s",
                (job.id,),
            )

        self.assertEqual(queue.block_stale_running(60), 1)
        self.assertIsNone(queue.next())
        with psycopg.connect(self.database_url) as conn:
            row = conn.execute(
                "SELECT status,error FROM cozy_jobs WHERE id=%s", (job.id,)
            ).fetchone()
        self.assertEqual(row[0], JobStatus.BLOCKED.value)
        self.assertEqual(row[1], "stale_running_job_requires_review")

    def test_job_claim_is_atomic(self):
        queue_a = PostgresJobQueue(self.database_url)
        queue_b = PostgresJobQueue(self.database_url)
        job = Job(
            JobType.PLAN_BOOK,
            {"project_id": str(uuid4())},
        )
        queue_a.enqueue(job)

        claimed = queue_a.next()
        second_claim = queue_b.next()

        self.assertIsNotNone(claimed)
        self.assertEqual(claimed.id, job.id)
        self.assertEqual(claimed.status, JobStatus.RUNNING)
        self.assertEqual(claimed.attempts, 1)
        self.assertIsNotNone(claimed.claim_token)
        self.assertIsNone(second_claim)

    def test_stale_worker_cannot_save_after_claim_is_invalidated(self):
        queue = PostgresJobQueue(self.database_url)
        job = Job(JobType.PLAN_BOOK, {"project_id": str(uuid4())})
        queue.enqueue(job)
        claimed = queue.next()
        self.assertIsNotNone(claimed.claim_token)

        self.assertEqual(queue.block_stale_running(1), 0)
        import psycopg
        with psycopg.connect(self.database_url) as conn:
            conn.execute(
                "UPDATE cozy_jobs SET updated_at=NOW() - INTERVAL '1 hour' WHERE id=%s",
                (job.id,),
            )
        self.assertEqual(queue.block_stale_running(60), 1)

        claimed.succeed()
        with self.assertRaisesRegex(RuntimeError, "job_claim_lost"):
            queue.save(claimed)


if __name__ == "__main__":
    unittest.main()
