import unittest

from backend.domain.models import Scene
from backend.domain.states import QAResult
from backend.jobs.models import Job, JobStatus, JobType
from backend.jobs.queue import InMemoryJobQueue
from backend.production.pipeline import ScenePipeline


class JobTests(unittest.TestCase):
    def test_job_lifecycle(self):
        job = Job(JobType.GENERATE_SCENE, {"scene": 1})
        job.start()
        self.assertEqual(job.status, JobStatus.RUNNING)
        job.succeed()
        self.assertEqual(job.status, JobStatus.SUCCEEDED)

    def test_queue(self):
        queue = InMemoryJobQueue()
        job = queue.enqueue(Job(JobType.PLAN_BOOK, {}))
        self.assertIs(queue.next(), job)


class PipelineTests(unittest.TestCase):
    def test_locked_scene_creates_no_work(self):
        scene = Scene(1, "Room")
        scene.record_generation()
        scene.qa(QAResult.PASS)
        self.assertEqual(ScenePipeline().jobs_for("p", 1, scene), [])

    def test_regenerate_creates_new_generation_job(self):
        scene = Scene(1, "Room")
        scene.record_generation()
        job = ScenePipeline().apply_review(scene, QAResult.REGENERATE, "broken perspective")
        self.assertEqual(job.type, JobType.GENERATE_SCENE)
        self.assertEqual(job.payload["mode"], "REGENERATE")


if __name__ == "__main__":
    unittest.main()
