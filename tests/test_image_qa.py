import tempfile
import unittest
from pathlib import Path

from backend.prepress.image_qa import inspect_line_art


class ImageQATests(unittest.TestCase):
    def test_clean_binary_image_passes(self):
        try:
            from PIL import Image,ImageDraw
        except ImportError:
            self.skipTest("Pillow not installed")
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"art.png"
            im=Image.new("L",(2400,2400),255)
            ImageDraw.Draw(im).rectangle((300,300,2100,2100),outline=0,width=12)
            im.save(p)
            report=inspect_line_art(str(p))
            self.assertTrue(report.passed)


if __name__=="__main__": unittest.main()
