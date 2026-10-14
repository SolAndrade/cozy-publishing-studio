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

    def test_stale_project_copy_cannot_overwrite_newer_save(self):
        store_a = PostgresProjectStore(self.database_url)
        project = PublishingProject(
            Series("Concurrent Series", [Book(f"Book {i}", "Subtitle", i) for i in range(1, 6)])
        )
        store_a.save(project)

        store_b = PostgresProjectStore(self.database_url)
        copy_a = store_a.load(project.id)
        copy_b = store_b.load(project.id)

        copy_a.series.name = "First writer"
        store_a.save(copy_a)

        copy_b.series.name = "Stale second writer"
        with self.assertRaisesRegex(RuntimeError, "project_write_conflict"):
            store_b.save(copy_b)

        self.assertEqual(store_a.load(project.id).series.name, "First writer")

    def test_reviewed_blocked_job_can_be_explicitly_requeued(self):
        import psycopg
        queue = PostgresJobQueue(self.database_url)
        job = Job(JobType.PLAN_BOOK, {"project_id": str(uuid4())}, max_attempts=3)
        queue.enqueue(job)
        claimed = queue.next()
        with psycopg.connect(self.database_url) as conn:
            conn.execute(
                "UPDATE cozy_jobs SET updated_at=NOW() - INTERVAL '1 hour' WHERE id=%s",
                (claimed.id,),
            )
        self.assertEqual(queue.block_stale_running(60), 1)

        queue.requeue_blocked(job.id)
        retried = queue.next()
        self.assertEqual(retried.id, job.id)
        self.assertEqual(retried.attempts, 2)

    def test_exhausted_blocked_job_cannot_be_manually_requeued(self):
        import psycopg
        queue = PostgresJobQueue(self.database_url)
        job = Job(
            JobType.PLAN_BOOK,
            {"project_id": str(uuid4())},
            attempts=2,
            max_attempts=3,
        )
        queue.enqueue(job)
        claimed = queue.next()
        with psycopg.connect(self.database_url) as conn:
            conn.execute(
                "UPDATE cozy_jobs SET updated_at=NOW() - INTERVAL '1 hour' WHERE id=%s",
                (claimed.id,),
            )
        self.assertEqual(queue.block_stale_running(60), 1)

        with self.assertRaisesRegex(RuntimeError, "job_not_requeueable"):
            queue.requeue_blocked(job.id)

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

    def test_stale_claim_is_requeued_with_new_fence(self):
        import psycopg
        queue = PostgresJobQueue(self.database_url)
        job = Job(JobType.PLAN_BOOK, {"project_id": str(uuid4())}, max_attempts=3)
        queue.enqueue(job)
        first = queue.next()
        old_token = first.claim_token
        with psycopg.connect(self.database_url) as conn:
            conn.execute(
                "UPDATE cozy_jobs SET updated_at=NOW() - INTERVAL '1 hour' WHERE id=%s",
                (job.id,),
            )

        self.assertEqual(queue.recover_stale_running(60), (1, 0))
        second = queue.next()
        self.assertEqual(second.id, job.id)
        self.assertEqual(second.attempts, 2)
        self.assertNotEqual(second.claim_token, old_token)

        first.succeed()
        with self.assertRaisesRegex(RuntimeError, "job_claim_lost"):
            queue.save(first)

    def test_stale_claim_at_retry_limit_is_blocked(self):
        import psycopg
        queue = PostgresJobQueue(self.database_url)
        job = Job(
            JobType.PLAN_BOOK,
            {"project_id": str(uuid4())},
            attempts=2,
            max_attempts=3,
        )
        queue.enqueue(job)
        claimed = queue.next()
        self.assertEqual(claimed.attempts, 3)
        with psycopg.connect(self.database_url) as conn:
            conn.execute(
                "UPDATE cozy_jobs SET updated_at=NOW() - INTERVAL '1 hour' WHERE id=%s",
                (job.id,),
            )

        self.assertEqual(queue.recover_stale_running(60), (0, 1))
        self.assertIsNone(queue.next())

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
