import os
import tempfile
import unittest
from unittest.mock import patch

from backend.jobs.queue import FileJobQueue
from backend.runtime_factory import runtime_from_env
from backend.storage.file_store import FileProjectStore


class RuntimeFactoryTests(unittest.TestCase):
    def test_development_uses_local_durable_runtime(self):
        with tempfile.TemporaryDirectory() as d:
            env={
                "COZY_ENV":"development",
                "COZY_PROJECTS_DIR":f"{d}/projects",
                "COZY_JOBS_DIR":f"{d}/jobs",
            }
            with patch.dict(os.environ,env,clear=True):
                runtime=runtime_from_env()
            self.assertIsInstance(runtime.store,FileProjectStore)
            self.assertIsInstance(runtime.queue,FileJobQueue)

    def test_production_without_database_fails_closed(self):
        with patch.dict(os.environ,{"COZY_ENV":"production"},clear=True):
            with self.assertRaisesRegex(RuntimeError,"DATABASE_URL"):
                runtime_from_env()


if __name__=="__main__":
    unittest.main()
