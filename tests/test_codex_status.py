from pathlib import Path
import json
import tempfile
import unittest
from unittest.mock import patch

from agent_orchestrator.codex_status import (
    capture_status_snapshot,
    default_status_command,
    write_status_delta,
)
from agent_orchestrator.shell import CommandResult


class CodexStatusTests(unittest.TestCase):
    def test_default_status_command_accepts_missing_command(self):
        self.assertIsNone(default_status_command({"codex": {}}))
        self.assertIsNone(default_status_command({"codex": {"status_command": None}}))

    def test_default_status_command_accepts_list(self):
        self.assertEqual(
            default_status_command({"codex": {"status_command": ["codex", "status", "--json"]}}),
            ["codex", "status", "--json"],
        )

    def test_missing_status_command_writes_unavailable_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "codex-status-before.json"

            snapshot = capture_status_snapshot(
                output_path=output_path,
                label="before",
                config={"codex": {}},
            )

            self.assertFalse(snapshot["available"])
            self.assertEqual(snapshot["label"], "before")
            self.assertIsNone(snapshot["command"])
            saved = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertFalse(saved["available"])
            self.assertIn("No codex.status_command configured", saved["reason"])

    def test_configured_status_command_writes_output_and_parsed_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "codex-status-after.json"

            def fake_run_command(args, *, cwd=None, input_text=None, check=True, env=None):
                self.assertEqual(args, ["codex", "status", "--json"])
                return CommandResult(args, 0, '{"remaining": 42}', "")

            with patch("agent_orchestrator.codex_status.run_command", fake_run_command):
                snapshot = capture_status_snapshot(
                    output_path=output_path,
                    label="after",
                    config={"codex": {"status_command": ["codex", "status", "--json"]}},
                )

            self.assertTrue(snapshot["available"])
            self.assertEqual(snapshot["parsed"], {"remaining": 42})
            saved = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(saved["stdout"], '{"remaining": 42}')
            self.assertEqual(saved["parsed"], {"remaining": 42})

    def test_write_status_delta_links_snapshots(self):
        with tempfile.TemporaryDirectory() as tmp:
            before = Path(tmp) / "before.json"
            after = Path(tmp) / "after.json"
            delta_path = Path(tmp) / "delta.json"
            before.write_text(json.dumps({"available": True}), encoding="utf-8")
            after.write_text(json.dumps({"available": False}), encoding="utf-8")

            delta = write_status_delta(before_path=before, after_path=after, output_path=delta_path)

            self.assertFalse(delta["available"])
            self.assertEqual(delta["before"], str(before))
            self.assertEqual(delta["after"], str(after))
            self.assertTrue(delta_path.exists())


if __name__ == "__main__":
    unittest.main()
