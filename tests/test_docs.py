from pathlib import Path
import unittest


class DocsTests(unittest.TestCase):
    def test_connector_docs_exist_and_contain_core_terms(self):
        repo = Path(__file__).resolve().parents[1]
        docs = {
            "docs/GITHUB_CONNECTOR_WORKFLOW.md": ["GitHub connector", "merge into `main`", "local orchestrator"],
            "docs/REPO_MAP.md": ["README.md", "agent_orchestrator/orchestrator.py", "docs/examples/fractal-mvp-issue.md"],
            "docs/LABELS.md": ["agent-run", "agent-ready-for-human", "agent-done"],
            "docs/REVIEW_PROTOCOL.md": ["request changes", "approve", "Merge into `main`"],
        }

        for rel_path, phrases in docs.items():
            path = repo / rel_path
            self.assertTrue(path.exists(), rel_path)
            text = path.read_text(encoding="utf-8")
            for phrase in phrases:
                self.assertIn(phrase, text, f"{rel_path} missing {phrase!r}")

    def test_test_note_removed(self):
        repo = Path(__file__).resolve().parents[1]
        self.assertFalse((repo / "docs/test-note.md").exists())


if __name__ == "__main__":
    unittest.main()
