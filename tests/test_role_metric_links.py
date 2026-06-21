from datetime import datetime, timezone
from pathlib import Path
import json
import os
import tempfile
import unittest
from unittest.mock import patch

from agent_orchestrator import state as state_module
from agent_orchestrator.state import RunState


class RoleMetricLinkTests(unittest.TestCase):
    def test_run_json_links_existing_role_metrics(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(state_module, "STATE_ROOT", Path(tmp)):
                run = RunState(issue=9, branch="agent/issue-9")
                run.run_dir.mkdir(parents=True, exist_ok=True)
                planner = run.run_dir / "planner.md"
                planner.write_text("planner", encoding="utf-8")
                planner.with_suffix(planner.suffix + ".metrics.json").write_text("{}", encoding="utf-8")
                run.planner_output = str(planner)
                run.save()

                data = json.loads(run.run_json_path.read_text(encoding="utf-8"))
                self.assertEqual(
                    data["artifacts"]["role_metrics"]["planner"],
                    str(planner.with_suffix(planner.suffix + ".metrics.json")),
                )

    def test_run_json_and_summary_aggregate_codex_usage(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(state_module, "STATE_ROOT", Path(tmp)):
                run = RunState(issue=15, branch="agent/issue-15")
                run.run_dir.mkdir(parents=True, exist_ok=True)
                planner = run.run_dir / "planner.md"
                builder = run.run_dir / "builder-cycle-1.md"
                reviewer = run.run_dir / "reviewer-cycle-1.md"
                for path in (planner, builder, reviewer):
                    path.write_text(path.name, encoding="utf-8")
                planner.with_suffix(planner.suffix + ".metrics.json").write_text(
                    json.dumps(
                        {
                            "role": "planner",
                            "output_path": str(planner),
                            "usage_source": "codex-jsonl-turn.completed",
                            "codex_usage": {
                                "input_tokens": 100,
                                "cached_input_tokens": 80,
                                "output_tokens": 10,
                                "reasoning_output_tokens": 4,
                                "total_tokens": 110,
                            },
                        }
                    ),
                    encoding="utf-8",
                )
                builder.with_suffix(builder.suffix + ".metrics.json").write_text(
                    json.dumps(
                        {
                            "role": "builder",
                            "output_path": str(builder),
                            "usage_source": "codex-jsonl-turn.completed",
                            "codex_usage": {
                                "input_tokens": 200,
                                "cached_input_tokens": 150,
                                "output_tokens": 20,
                                "reasoning_output_tokens": 6,
                                "total_tokens": 220,
                            },
                        }
                    ),
                    encoding="utf-8",
                )
                reviewer.with_suffix(reviewer.suffix + ".metrics.json").write_text(
                    json.dumps(
                        {
                            "role": "reviewer",
                            "output_path": str(reviewer),
                            "usage_source": "codex-jsonl-turn.completed",
                            "codex_usage": {
                                "input_tokens": 50,
                                "cached_input_tokens": 20,
                                "output_tokens": 5,
                                "reasoning_output_tokens": 1,
                                "total_tokens": 55,
                            },
                        }
                    ),
                    encoding="utf-8",
                )
                run.planner_output = str(planner)
                run.builder_output = str(builder)
                run.reviewer_output = str(reviewer)
                run.save()

                data = json.loads(run.run_json_path.read_text(encoding="utf-8"))
                totals = data["token_usage"]["totals"]
                self.assertEqual(totals["input_tokens"], 350)
                self.assertEqual(totals["cached_input_tokens"], 250)
                self.assertEqual(totals["uncached_input_tokens"], 100)
                self.assertEqual(totals["output_tokens"], 35)
                self.assertEqual(totals["reasoning_output_tokens"], 11)
                self.assertEqual(totals["total_tokens"], 385)
                self.assertEqual(data["token_usage"]["roles"][1]["role"], "builder")
                self.assertEqual(data["token_usage"]["roles"][1]["cycle"], 1)

                summary = run.summary_path.read_text(encoding="utf-8")
                self.assertIn("## Token usage", summary)
                self.assertIn("| builder | 1 | 200 | 150 | 50 | 20 | 6 | 220 |", summary)
                self.assertIn("| **Total** |  | **350** | **250** | **100** | **35** | **11** | **385** |", summary)

    def test_token_usage_ignores_stale_metrics_from_previous_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(state_module, "STATE_ROOT", Path(tmp)):
                started = datetime.now(timezone.utc)
                run = RunState(
                    issue=15,
                    branch="agent/issue-15",
                    cycle=1,
                    started_at=started.isoformat(timespec="seconds"),
                )
                run.run_dir.mkdir(parents=True, exist_ok=True)
                current_builder = run.run_dir / "builder-cycle-1.md"
                stale_builder = run.run_dir / "builder-cycle-2.md"
                for path in (current_builder, stale_builder):
                    path.write_text(path.name, encoding="utf-8")
                current_builder.with_suffix(current_builder.suffix + ".metrics.json").write_text(
                    json.dumps(
                        {
                            "role": "builder",
                            "output_path": str(current_builder),
                            "usage_source": "codex-jsonl-turn.completed",
                            "codex_usage": {
                                "input_tokens": 100,
                                "cached_input_tokens": 90,
                                "output_tokens": 10,
                                "reasoning_output_tokens": 1,
                                "total_tokens": 110,
                            },
                        }
                    ),
                    encoding="utf-8",
                )
                stale_metrics = stale_builder.with_suffix(stale_builder.suffix + ".metrics.json")
                stale_metrics.write_text(
                    json.dumps(
                        {
                            "role": "builder",
                            "output_path": str(stale_builder),
                            "usage_source": "codex-jsonl-turn.completed",
                            "codex_usage": {
                                "input_tokens": 999,
                                "cached_input_tokens": 999,
                                "output_tokens": 999,
                                "reasoning_output_tokens": 999,
                                "total_tokens": 1998,
                            },
                        }
                    ),
                    encoding="utf-8",
                )
                old_timestamp = started.timestamp() - 60
                os.utime(stale_metrics, (old_timestamp, old_timestamp))
                run.builder_output = str(current_builder)
                run.save()

                data = json.loads(run.run_json_path.read_text(encoding="utf-8"))
                roles = data["token_usage"]["roles"]
                self.assertEqual(len(roles), 1)
                self.assertEqual(roles[0]["cycle"], 1)
                self.assertEqual(data["token_usage"]["totals"]["input_tokens"], 100)
                summary = run.summary_path.read_text(encoding="utf-8")
                self.assertNotIn("999", summary)


if __name__ == "__main__":
    unittest.main()
