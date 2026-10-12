import unittest

from backend.book_design.cover_package import CoverBuildRequest,CoverContent,prepare_cover
from backend.book_design.profiles import CLASSIC_PORTRAIT,COZY_SQUARE


class CoverPackageTests(unittest.TestCase):
    def content(self): return CoverContent("Title","Subtitle","Heading","Copy",1,(10,17,26))

    def test_square_and_portrait_use_profile_geometry(self):
        square=prepare_cover(CoverBuildRequest(COZY_SQUARE,80,.18,self.content()))
        portrait=prepare_cover(CoverBuildRequest(CLASSIC_PORTRAIT,80,.18,self.content()))
        self.assertAlmostEqual(square.full_height_in,8.75)
        self.assertAlmostEqual(portrait.full_height_in,11.25)
        self.assertAlmostEqual(square.full_width_in,portrait.full_width_in)

    def test_duplicate_cover_scene_rejected(self):
        bad=CoverContent("T","S","H","C",1,(1,2,3))
        with self.assertRaises(ValueError): prepare_cover(CoverBuildRequest(COZY_SQUARE,80,.18,bad))


if __name__=="__main__": unittest.main()
