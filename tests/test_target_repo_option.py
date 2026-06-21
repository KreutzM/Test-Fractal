import unittest

from agent_orchestrator.cli import build_parser


class TargetRepoOptionTests(unittest.TestCase):
    def test_run_parser_accepts_repo_option(self):
        parser = build_parser()
        args = parser.parse_args(["run", "--issue", "123", "--repo", "C:/tmp/target"])
        self.assertEqual(args.command, "run")
        self.assertEqual(args.issue, 123)
        self.assertEqual(args.repo, "C:/tmp/target")


if __name__ == "__main__":
    unittest.main()
