import unittest
from backend.publishing.readiness import publishing_readiness,RequirementState


class ReadinessTests(unittest.TestCase):
    def test_kdp_connector_blocks_machine_readiness(self):
        r=publishing_readiness(interior_locked=True,cover_locked=True,metadata_ready=True,ai_declaration_ready=True,kdp_draft_connector_ready=False)
        self.assertFalse(r.machine_ready)
        self.assertEqual(r.human_actions[0].name,"Final publish")
        self.assertEqual(r.human_actions[0].state,RequirementState.HUMAN)


if __name__=="__main__": unittest.main()
