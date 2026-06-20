import unittest

from agent_orchestrator.orchestrator import _review_decision


class ReviewDecisionTests(unittest.TestCase):
    def test_approve_marker(self):
        self.assertEqual(_review_decision("Looks good\nREVIEW_DECISION: approve"), "approve")

    def test_request_changes_marker(self):
        self.assertEqual(_review_decision("REVIEW_DECISION: request_changes"), "request_changes")

    def test_block_marker(self):
        self.assertEqual(_review_decision("REVIEW_DECISION: block"), "block")

    def test_default_is_request_changes(self):
        self.assertEqual(_review_decision("unclear"), "request_changes")


if __name__ == "__main__":
    unittest.main()
