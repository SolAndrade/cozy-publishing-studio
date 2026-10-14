import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from backend.workers.app import recover_stale_jobs


class RecordingQueue:
    def __init__(self):
        self.recovered = []
        self.blocked = []

    def recover_stale_running(self, seconds):
        self.recovered.append(seconds)

    def block_stale_running(self, seconds):
        self.blocked.append(seconds)


class WorkerRecoveryTests(unittest.TestCase):
    def test_development_requeues_stale_jobs(self):
        queue = RecordingQueue()
        with patch.dict(os.environ, {"COZY_ENV": "development"}, clear=True):
            recover_stale_jobs(SimpleNamespace(queue=queue), 900)
        self.assertEqual(queue.recovered, [900])
        self.assertEqual(queue.blocked, [])

    def test_production_blocks_stale_jobs_instead_of_replaying_paid_work(self):
        queue = RecordingQueue()
        with patch.dict(os.environ, {"COZY_ENV": "production"}, clear=True):
            recover_stale_jobs(SimpleNamespace(queue=queue), 900)
        self.assertEqual(queue.recovered, [])
        self.assertEqual(queue.blocked, [900])


if __name__ == "__main__":
    unittest.main()
