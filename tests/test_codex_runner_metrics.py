from pathlib import Path
import json
import os
import tempfile
import unittest
from unittest.mock import patch

from agent_orchestrator.codex_runner import _extract_usage_from_events, run_codex_role
from agent_orchestrator.shell import CommandResult, TARGET_REPO_ENV


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

    def test_extract_usage_from_turn_completed_event(self):
        events = "\n".join(
            [
                json.dumps({"type": "turn.started"}),
                json.dumps(
                    {
                        "type": "turn.completed",
                        "usage": {
                            "input_tokens": 100,
                            "cached_input_tokens": 40,
                            "output_tokens": 20,
                            "reasoning_output_tokens": 7,
                        },
                    }
                ),
            ]
        )

        usage = _extract_usage_from_events(events)

        self.assertEqual(
            usage,
            {
                "input_tokens": 100,
                "cached_input_tokens": 40,
                "output_tokens": 20,
                "reasoning_output_tokens": 7,
                "total_tokens": 120,
            },
        )

    def test_json_mode_writes_events_stderr_and_actual_usage(self):
        with tempfile.TemporaryDirectory() as tmp:
            prompt_dir = Path(tmp) / "prompts"
            prompt_dir.mkdir()
            (prompt_dir / "builder.md").write_text("Build $thing", encoding="utf-8")
            output_path = Path(tmp) / "builder-cycle-1.md"
            output_path.write_text("final answer", encoding="utf-8")
            events = json.dumps(
                {
                    "type": "turn.completed",
                    "usage": {
                        "input_tokens": 10,
                        "cached_input_tokens": 2,
                        "output_tokens": 3,
                        "reasoning_output_tokens": 1,
                    },
                }
            )

            def fake_run_command(args, *, cwd=None, input_text=None, check=True, env=None):
                self.assertIn("--json", args)
                return CommandResult(args, 0, events + "\n", "debug text")

            with (
                patch("agent_orchestrator.codex_runner.PROMPT_DIR", prompt_dir),
                patch("agent_orchestrator.codex_runner.run_command", fake_run_command),
            ):
                result = run_codex_role(
                    role="builder",
                    variables={"thing": "feature"},
                    model="test-model",
                    sandbox="workspace-write",
                    approval="never",
                    output_path=output_path,
                )

            self.assertTrue(result.ok)
            self.assertEqual(output_path.with_suffix(output_path.suffix + ".events.jsonl").read_text(encoding="utf-8"), events + "\n")
            self.assertEqual(output_path.with_suffix(output_path.suffix + ".stderr.txt").read_text(encoding="utf-8"), "debug text")
            metrics = json.loads(output_path.with_suffix(output_path.suffix + ".metrics.json").read_text(encoding="utf-8"))
            self.assertEqual(metrics["events_path"], str(output_path.with_suffix(output_path.suffix + ".events.jsonl")))
            self.assertEqual(metrics["stderr_path"], str(output_path.with_suffix(output_path.suffix + ".stderr.txt")))
            self.assertEqual(metrics["usage_source"], "codex-jsonl-turn.completed")
            self.assertEqual(metrics["codex_usage"]["input_tokens"], 10)
            self.assertEqual(metrics["codex_usage"]["output_tokens"], 3)
            self.assertEqual(metrics["codex_usage"]["total_tokens"], 13)

    def test_target_repo_env_controls_codex_workdir_but_keeps_output_absolute(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target_repo = root / "target"
            target_repo.mkdir()
            prompt_dir = root / "prompts"
            prompt_dir.mkdir()
            (prompt_dir / "reviewer.md").write_text("Review $thing", encoding="utf-8")
            output_path = root / "runs" / "reviewer-cycle-1.md"
            events = json.dumps({"type": "turn.completed", "usage": {"input_tokens": 1, "output_tokens": 2}})

            def fake_run_command(args, *, cwd=None, input_text=None, check=True, env=None):
                self.assertEqual(Path(cwd).resolve(), target_repo.resolve())
                self.assertEqual(args[args.index("--cd") + 1], str(target_repo.resolve()))
                self.assertEqual(args[args.index("--output-last-message") + 1], str(output_path.resolve()))
                return CommandResult(args, 0, events + "\n", "")

            with (
                patch.dict(os.environ, {TARGET_REPO_ENV: str(target_repo)}),
                patch("agent_orchestrator.codex_runner.PROMPT_DIR", prompt_dir),
                patch("agent_orchestrator.codex_runner.run_command", fake_run_command),
            ):
                result = run_codex_role(
                    role="reviewer",
                    variables={"thing": "feature"},
                    model="test-model",
                    sandbox="read-only",
                    approval="never",
                    output_path=output_path,
                )

            self.assertTrue(result.ok)
            self.assertTrue(output_path.with_suffix(output_path.suffix + ".metrics.json").exists())


if __name__ == "__main__":
    unittest.main()
