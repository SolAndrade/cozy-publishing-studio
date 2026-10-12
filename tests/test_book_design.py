import unittest

from backend.book_design.cover import CoverSpec,build_cover_plan
from backend.book_design.interior import InteriorSpec,build_interior_plan


class BookDesignTests(unittest.TestCase):
    def test_square_interior_has_80_pages(self):
        plan=build_interior_plan()
        self.assertEqual(plan.page_count,80)
        self.assertEqual([p.page_number for p in plan.pages if p.scene_number][:3],[1,3,5])
        self.assertTrue(plan.pages[-1].blank)

    def test_cover_math_matches_square_template_shape(self):
        plan=build_cover_plan(CoverSpec(8.5,8.5,80,.18))
        self.assertAlmostEqual(plan.full_width_in,17.43,places=2)
        self.assertAlmostEqual(plan.full_height_in,8.75,places=2)
        self.assertTrue(plan.barcode_reserved)

    def test_non_40_scene_template_rejected(self):
        with self.assertRaises(ValueError):
            build_interior_plan(InteriorSpec(scene_count=39))


if __name__=="__main__": unittest.main()
