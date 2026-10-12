import unittest
from backend.planners.ai_manifest import build_manifest

class FakeProvider:
    def complete_json(self, instructions, prompt):
        return {"scenes": [f"Scene {i}" for i in range(1, 41)]}

class ManifestTests(unittest.TestCase):
    def test_exactly_40(self):
        self.assertEqual(len(build_manifest(FakeProvider(), "Book", "Sub", "Brief")), 40)

if __name__ == "__main__":
    unittest.main()
