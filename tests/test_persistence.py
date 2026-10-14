import tempfile
import unittest

from backend.orchestrator.engine import ProductionEngine
from backend.runtime import Runtime
from backend.storage.file_store import FileProjectStore


class PersistenceTests(unittest.TestCase):
    def test_round_trip_project(self):
        engine=ProductionEngine()
        project=engine.create_series("Series",[(f"Book {i}","Sub") for i in range(1,6)])
        book=project.series.books[0]\n        engine.install_manifest(book,[f"Scene {i}" for i in range(1,41)])\n        book.locked_brief="Locked village identity"\n        book.scenes[0].image_artifact={"key":"projects/p/books/1/scenes/1/generation-1.png","sha256":"abc"}
        with tempfile.TemporaryDirectory() as d:
            store=FileProjectStore(d); store.save(project); loaded=store.load(project.id)
        self.assertEqual(loaded.series.name,"Series")
        self.assertEqual(len(loaded.series.books[0].scenes),40)\n        self.assertEqual(loaded.series.books[0].locked_brief,"Locked village identity")\n        self.assertEqual(loaded.series.books[0].scenes[0].image_artifact["sha256"],"abc")

    def test_runtime_reloads_project_after_restart(self):
        engine=ProductionEngine()
        project=engine.create_series("Series",[(f"Book {i}","Sub") for i in range(1,6)])
        with tempfile.TemporaryDirectory() as d:
            first=Runtime(store=FileProjectStore(d))
            first.add(project)
            second=Runtime(store=FileProjectStore(d))
            loaded=second.get(project.id)
        self.assertEqual(loaded.id,project.id)
        self.assertEqual(loaded.series.name,"Series")


if __name__=="__main__": unittest.main()
