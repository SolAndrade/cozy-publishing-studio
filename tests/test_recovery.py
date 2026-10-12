import unittest

from backend.domain.states import QAResult
from backend.jobs.models import JobType
from backend.orchestrator.engine import ProductionEngine
from backend.production.recovery import recovery_job


class RecoveryTests(unittest.TestCase):
    def test_resume_at_first_unlocked(self):
        e=ProductionEngine()
        p=e.create_series("S",[(f"B{i}","") for i in range(1,6)])
        b=p.series.books[0]
        e.install_manifest(b,[f"Scene {i}" for i in range(1,41)])
        e.start_generation(b)
        b.scenes[0].record_generation(); b.scenes[0].qa(QAResult.PASS)
        job=recovery_job(p.id,b)
        self.assertEqual(job.type,JobType.GENERATE_SCENE)
        self.assertEqual(job.payload["scene_number"],2)


if __name__=="__main__": unittest.main()
