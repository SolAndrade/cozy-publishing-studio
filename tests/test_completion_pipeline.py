import unittest

from backend.domain.states import BookState,QAResult
from backend.orchestrator.completion import *
from backend.orchestrator.engine import ProductionEngine


class CompletionTests(unittest.TestCase):
    def test_post_art_flow(self):
        e=ProductionEngine(); p=e.create_series("S",[(f"B{i}","") for i in range(1,6)])
        b=p.series.books[0]; e.install_manifest(b,[f"S{i}" for i in range(1,41)]); e.start_generation(b)
        for s in b.scenes: s.record_generation(); s.qa(QAResult.PASS)
        b.advance(BookState.ART_LOCKED)
        advance_after_art(b,True); self.assertEqual(b.state,BookState.PREPRESS_PASS)
        advance_after_interior(b,True); self.assertEqual(b.state,BookState.INTERIOR_LOCKED)
        advance_after_cover(b,True); self.assertEqual(b.state,BookState.COVER_LOCKED)
        advance_after_metadata(b,True); self.assertEqual(b.state,BookState.METADATA_READY)

    def test_failed_preflight_blocks_transition(self):
        e=ProductionEngine(); p=e.create_series("S",[(f"B{i}","") for i in range(1,6)])
        b=p.series.books[0]; b.state=BookState.PREPRESS_PASS
        with self.assertRaises(ValueError): advance_after_interior(b,False)


if __name__=="__main__": unittest.main()
