from pathlib import Path
import os
import tempfile
import unittest
from unittest.mock import patch

from agent_orchestrator import github_ops
from agent_orchestrator.shell import CommandResult, TARGET_REPO_ENV


class GithubOpsTargetRepoTests(unittest.TestCase):
    def test_gh_default_cwd_ignores_target_repo_env(self):
        with tempfile.TemporaryDirectory() as tmp:
            target_repo = Path(tmp) / "target"
            target_repo.mkdir()
            observed = {}

            def fake_run_command(args, *, cwd=None, check=True):
                observed["args"] = args
                observed["cwd"] = cwd
                return CommandResult(args, 0, "{}", "")

            with (
                patch.dict(os.environ, {TARGET_REPO_ENV: str(target_repo)}),
                patch.object(github_ops, "ORCHESTRATOR_REPO_ROOT", Path("C:/orchestrator")),
                patch("agent_orchestrator.github_ops.run_command", fake_run_command),
            ):
                github_ops.gh(["issue", "view", "21"])

        self.assertEqual(observed["args"], ["gh", "issue", "view", "21"])
        self.assertEqual(observed["cwd"], Path("C:/orchestrator"))


if __name__ == "__main__":
    unittest.main()
