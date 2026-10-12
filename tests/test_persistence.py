import tempfile
import unittest

from backend.orchestrator.engine import ProductionEngine
from backend.storage.file_store import FileProjectStore


class PersistenceTests(unittest.TestCase):
    def test_round_trip_project(self):
        engine=ProductionEngine()
        project=engine.create_series("Series",[(f"Book {i}","Sub") for i in range(1,6)])
        engine.install_manifest(project.series.books[0],[f"Scene {i}" for i in range(1,41)])
        with tempfile.TemporaryDirectory() as d:
            store=FileProjectStore(d); store.save(project); loaded=store.load(project.id)
        self.assertEqual(loaded.series.name,"Series")
        self.assertEqual(len(loaded.series.books[0].scenes),40)


if __name__=="__main__": unittest.main()
