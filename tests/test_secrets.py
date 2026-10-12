import os,unittest
from unittest.mock import patch
from backend.security.secrets import require_secret,secret_status


class SecretTests(unittest.TestCase):
    def test_missing_secret_is_explicit(self):
        with patch.dict(os.environ,{},clear=True):
            with self.assertRaises(RuntimeError): require_secret("COZY_IMAGE_API_KEY")
            self.assertFalse(secret_status(("COZY_IMAGE_API_KEY",))[0].configured)


if __name__=="__main__": unittest.main()
