import unittest
from dataclasses import replace

from backend.book_design.cover import CoverSpec,build_cover_plan
from backend.book_design.interior import build_interior_plan
from backend.book_design.profiles import COZY_SQUARE


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

    def test_non_40_scene_profile_is_supported(self):
        profile=replace(COZY_SQUARE,id="cozy-square-39",scene_count=39)
        plan=build_interior_plan(profile)
        self.assertEqual(plan.page_count,78)
        self.assertEqual(sum(p.scene_number is not None for p in plan.pages),39)


if __name__=="__main__": unittest.main()
