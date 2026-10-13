import os
import unittest
from unittest.mock import patch

from backend.providers.image_contract import GenerationRequest, build_coloring_prompt
from backend.providers.review_contract import normalize_review
from backend.providers.registry import ProviderState, provider_status


class ContractTests(unittest.TestCase):
    def test_prompt_contains_locked_constraints(self):
        prompt=build_coloring_prompt(GenerationRequest("p",1,4,"Corner cafe","square diorama"))
        self.assertIn("square diorama",prompt)
        self.assertIn("Scene 04",prompt)

    def test_review_rejects_vague_failure(self):
        with self.assertRaises(ValueError):
            normalize_review({"result":"REGENERATE","reason":""})

    def test_review_accepts_pass(self):
        self.assertEqual(normalize_review({"result":"PASS"})["result"],"PASS")

    def test_s3_storage_requires_bucket_and_credentials(self):
        env={
            "COZY_ARTIFACT_STORE":"s3",
            "COZY_S3_BUCKET":"private-books",
            "AWS_ACCESS_KEY_ID":"configured",
            "AWS_SECRET_ACCESS_KEY":"configured",
        }
        with patch.dict(os.environ,env,clear=True):
            storage=next(p for p in provider_status() if p.role=="storage")
        self.assertEqual(storage.state,ProviderState.CONFIGURED)

    def test_unknown_storage_adapter_is_blocked(self):
        with patch.dict(os.environ,{"COZY_ARTIFACT_STORE":"cloud"},clear=True):
            storage=next(p for p in provider_status() if p.role=="storage")
        self.assertEqual(storage.state,ProviderState.BLOCKED)


if __name__=="__main__": unittest.main()
