import subprocess
import sys
import unittest
from unittest.mock import patch

from core.cli import main as core_main


class CliVersionTests(unittest.TestCase):
    def test_module_version_flag_returns_version_and_exit_code_zero(self):
        completed = subprocess.run(
            [sys.executable, "-m", "core", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 0)
        self.assertTrue(completed.stdout.strip())
        self.assertEqual(completed.stderr, "")

    def test_core_cli_delegates_non_version_commands(self):
        with patch("core.cli._orchestrator_main", return_value=17) as orchestrator_main:
            exit_code = core_main(["doctor"])

        self.assertEqual(exit_code, 17)
        orchestrator_main.assert_called_once_with(["doctor"])


if __name__ == "__main__":
    unittest.main()
