import importlib
import os,unittest
from unittest.mock import patch
from backend.api.status import system_status


class APIStatusTests(unittest.TestCase):
    def test_status_never_exposes_secret_values(self):
        with patch.dict(os.environ,{"COZY_IMAGE_API_KEY":"super-secret","COZY_VISION_API_KEY":"vision-secret"},clear=True):
            payload=system_status()
            rendered=str(payload)
            self.assertNotIn("super-secret",rendered)
            self.assertNotIn("vision-secret",rendered)
            self.assertTrue(all("configured" in x for x in payload["secrets"]))

    def test_api_module_imports(self):
        module=importlib.import_module("backend.api.app")
        self.assertTrue(hasattr(module,"Handler"))


if __name__=="__main__": unittest.main()
