import unittest
from unittest.mock import patch

from agent_orchestrator.shell import CommandResult, resolve_executable, run_command


class ShellTests(unittest.TestCase):
    def test_windows_prefers_cmd_shim(self):
        def fake_which(name):
            if name == "codex.cmd":
                return r"C:\Users\Admin\AppData\Roaming\npm\codex.cmd"
            if name == "codex.exe":
                return None
            if name == "codex":
                return r"C:\Users\Admin\AppData\Roaming\npm\codex.ps1"
            return None

        with patch("agent_orchestrator.shell.os.name", "nt"), patch(
            "agent_orchestrator.shell.which", side_effect=fake_which
        ):
            args = resolve_executable(["codex", "--version"])

        self.assertEqual(args[0], r"C:\Users\Admin\AppData\Roaming\npm\codex.cmd")
        self.assertEqual(args[1], "--version")

    def test_file_not_found_returns_command_result_when_check_false(self):
        result = run_command(["definitely-not-a-real-command-for-agent-tests"], check=False)

        self.assertIsInstance(result, CommandResult)
        self.assertEqual(result.returncode, 127)
        self.assertIn("Executable not found", result.stderr)


if __name__ == "__main__":
    unittest.main()
