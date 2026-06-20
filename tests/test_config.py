from pathlib import Path
import tempfile
import unittest
import json

from agent_orchestrator.config import load_config, ConfigError


class ConfigTests(unittest.TestCase):
    def test_load_default_config(self):
        config = load_config("config/orchestrator.json")
        self.assertEqual(config["model"], "gpt-5.4-mini")
        self.assertIn("labels", config)

    def test_invalid_config_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text(json.dumps({"model": "gpt-5.4-mini"}), encoding="utf-8")
            with self.assertRaises(ConfigError):
                load_config(path)


if __name__ == "__main__":
    unittest.main()
