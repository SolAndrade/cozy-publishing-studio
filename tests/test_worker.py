import os
import unittest
from unittest.mock import patch

from backend.jobs.models import Job, JobStatus, JobType
from backend.jobs.queue import InMemoryJobQueue
from backend.runtime import Runtime
from backend.workers.runner import Worker
from backend.workers.service import build_worker
from backend.providers.factory import ProviderNotConfigured


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

    def test_production_worker_fails_closed_without_real_providers(self):
        with patch.dict(os.environ,{"COZY_ENV":"production"},clear=True):
            with self.assertRaises(ProviderNotConfigured):
                build_worker(Runtime())


if __name__ == "__main__":
    unittest.main()
