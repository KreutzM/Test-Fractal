from pathlib import Path
import json
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


if __name__ == "__main__":
    unittest.main()
