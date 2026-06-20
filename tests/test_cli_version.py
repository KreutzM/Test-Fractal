import subprocess
import sys
import unittest


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


if __name__ == "__main__":
    unittest.main()
