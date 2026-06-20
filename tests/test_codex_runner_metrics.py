from pathlib import Path
import json
import tempfile
import unittest
from unittest.mock import patch

from agent_orchestrator.codex_runner import run_codex_role


class CodexRunnerMetricsTests(unittest.TestCase):
    def test_dry_run_writes_metrics_sidecar(self):
        with tempfile.TemporaryDirectory() as tmp:
            prompt_dir = Path(tmp) / "prompts"
            prompt_dir.mkdir()
            (prompt_dir / "planner.md").write_text("Hello $name", encoding="utf-8")
            output_path = Path(tmp) / "planner.md"

            with patch("agent_orchestrator.codex_runner.PROMPT_DIR", prompt_dir):
                result = run_codex_role(
                    role="planner",
                    variables={"name": "world"},
                    model="test-model",
                    sandbox="read-only",
                    approval="never",
                    output_path=output_path,
                    dry_run=True,
                )

            self.assertTrue(result.ok)
            metrics_path = output_path.with_suffix(output_path.suffix + ".metrics.json")
            self.assertTrue(metrics_path.exists())
            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
            self.assertEqual(metrics["role"], "planner")
            self.assertEqual(metrics["model"], "test-model")
            self.assertEqual(metrics["sandbox"], "read-only")
            self.assertTrue(metrics["dry_run"])
            self.assertEqual(metrics["returncode"], 0)
            self.assertGreater(metrics["prompt_chars"], 0)
            self.assertGreater(metrics["output_chars"], 0)
            self.assertGreaterEqual(metrics["duration_ms"], 0)


if __name__ == "__main__":
    unittest.main()
