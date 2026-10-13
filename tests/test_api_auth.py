import os
import unittest
from unittest.mock import patch

from backend.security.api_auth import api_token_configured, authorize_header


class APIAuthTests(unittest.TestCase):
    def test_development_does_not_require_token(self):
        with patch.dict(os.environ,{"COZY_ENV":"development"},clear=True):
            self.assertTrue(authorize_header(None))

    def test_production_requires_configured_bearer_token(self):
        env={"COZY_ENV":"production","COZY_API_TOKEN":"secret-token"}
        with patch.dict(os.environ,env,clear=True):
            self.assertTrue(api_token_configured())
            self.assertFalse(authorize_header(None))
            self.assertFalse(authorize_header("Bearer wrong"))
            self.assertTrue(authorize_header("Bearer secret-token"))

    def test_production_fails_closed_without_secret(self):
        with patch.dict(os.environ,{"COZY_ENV":"production"},clear=True):
            self.assertFalse(api_token_configured())
            self.assertFalse(authorize_header("Bearer anything"))


if __name__=="__main__": unittest.main()
