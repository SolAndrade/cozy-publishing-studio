import unittest

from backend.domain.states import QAResult
from backend.orchestrator.engine import ProductionEngine
from backend.prepress.book_audit import audit_book


class BookAuditTests(unittest.TestCase):
    def test_locked_book_passes_audit(self):
        engine=ProductionEngine()
        project=engine.create_series("S",[(f"B{i}","") for i in range(1,6)])
        book=project.series.books[0]
        engine.install_manifest(book,[f"Scene {i}" for i in range(1,41)])
        engine.start_generation(book)
        for scene in book.scenes:
            scene.record_generation(); scene.qa(QAResult.PASS)
        self.assertTrue(audit_book(book).passed)


if __name__=="__main__": unittest.main()
