from pathlib import Path
import os
import tempfile
import unittest
from unittest.mock import patch

from agent_orchestrator import cli
from agent_orchestrator.cli import build_parser
from agent_orchestrator.shell import TARGET_REPO_ENV


class TargetRepoOptionTests(unittest.TestCase):
    def test_run_parser_accepts_repo_option(self):
        parser = build_parser()
        args = parser.parse_args(["run", "--issue", "123", "--repo", "C:/tmp/target"])
        self.assertEqual(args.command, "run")
        self.assertEqual(args.issue, 123)
        self.assertEqual(args.repo, "C:/tmp/target")

    def test_missing_target_repo_returns_clear_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing-target"
            with patch("builtins.print") as print_mock:
                code = cli.main(["run", "--issue", "123", "--repo", str(missing)])

        self.assertEqual(code, 1)
        printed = "\n".join(str(call.args[0]) for call in print_mock.call_args_list)
        self.assertIn("Target repository path does not exist", printed)

    def test_target_repo_env_is_restored_after_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            with patch.dict(os.environ, {}, clear=True), patch("agent_orchestrator.cli.run_issue", return_value=0) as run_issue:
                code = cli.main(["run", "--issue", "123", "--repo", str(target)])

        self.assertEqual(code, 0)
        run_issue.assert_called_once()
        self.assertNotIn(TARGET_REPO_ENV, os.environ)


if __name__ == "__main__":
    unittest.main()
