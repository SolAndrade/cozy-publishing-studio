import unittest

from backend.jobs.models import Job, JobStatus, JobType
from backend.jobs.queue import InMemoryJobQueue
from backend.workers.runner import Worker


class WorkerTests(unittest.TestCase):
    def test_worker_runs_registered_job(self):
        seen = []
        queue = InMemoryJobQueue()
        queue.enqueue(Job(JobType.PLAN_BOOK, {"book": 1}))
        worker = Worker(queue, {JobType.PLAN_BOOK: lambda payload: seen.append(payload["book"])})
        job = worker.run_one()
        self.assertEqual(job.status, JobStatus.SUCCEEDED)
        self.assertEqual(seen, [1])

    def test_worker_records_failure(self):
        queue = InMemoryJobQueue()
        queue.enqueue(Job(JobType.PLAN_BOOK, {}))
        worker = Worker(queue, {})
        job = worker.run_one()
        self.assertEqual(job.status, JobStatus.FAILED)
        self.assertIn("No handler", job.error)


if __name__ == "__main__":
    unittest.main()
