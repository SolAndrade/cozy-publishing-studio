import unittest

from backend.kdp.draft import DraftPackage
from backend.metadata.package import MetadataPackage


class MetadataTests(unittest.TestCase):
    def test_valid_draft_requires_human_approval(self):
        metadata = MetadataPackage("Title", "Subtitle", "Description", ["one", "two"])
        draft = DraftPackage(metadata, "interior.pdf", "cover.pdf")
        draft.validate()

    def test_cannot_disable_final_approval(self):
        metadata = MetadataPackage("Title", "Subtitle", "Description")
        draft = DraftPackage(metadata, "interior.pdf", "cover.pdf", False)
        with self.assertRaises(ValueError):
            draft.validate()


if __name__ == "__main__":
    unittest.main()
