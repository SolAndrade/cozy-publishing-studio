import unittest

from backend.providers.image_contract import GenerationRequest, build_coloring_prompt
from backend.providers.review_contract import normalize_review


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


if __name__=="__main__": unittest.main()
