import unittest

from agent_orchestrator.git_ops import forbidden_changes


class GitOpsTests(unittest.TestCase):
    def test_forbidden_exact_file(self):
        hits = forbidden_changes([".env", "src/app.py"], [".env"])
        self.assertEqual(hits, [".env"])

    def test_forbidden_directory(self):
        hits = forbidden_changes(["secrets/token.txt", "README.md"], ["secrets/"])
        self.assertEqual(hits, ["secrets/token.txt"])

    def test_allowed_file(self):
        hits = forbidden_changes(["src/app.py"], ["secrets/"])
        self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()
