import unittest

from backend.book_design.interior import build_interior_plan
from backend.book_design.profiles import CLASSIC_PORTRAIT,COZY_SQUARE,Orientation,custom_profile


class ProfileTests(unittest.TestCase):
    def test_square_profile(self):
        p=COZY_SQUARE
        self.assertEqual(p.orientation,Orientation.SQUARE)
        self.assertEqual(build_interior_plan(p).page_count,80)

    def test_portrait_profile(self):
        p=CLASSIC_PORTRAIT
        self.assertEqual(p.orientation,Orientation.PORTRAIT)
        self.assertEqual((p.trim_width_in,p.trim_height_in),(8.5,11.0))
        self.assertEqual(build_interior_plan(p).page_count,80)

    def test_custom_profile(self):
        p=custom_profile(trim_width_in=7,trim_height_in=10,art_width_in=6,art_height_in=9,scene_count=30,blank_reverse=True,bleed=False)
        self.assertEqual(p.physical_pages,60)

    def test_art_cannot_exceed_trim(self):
        with self.assertRaises(ValueError):
            custom_profile(trim_width_in=6,trim_height_in=9,art_width_in=7,art_height_in=8,scene_count=40,blank_reverse=True,bleed=False)


if __name__=="__main__": unittest.main()
