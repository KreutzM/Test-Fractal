import unittest

from agent_orchestrator.run_log import estimate_tokens, format_duration


class RunLogTests(unittest.TestCase):
    def test_estimate_tokens_is_stable(self):
        self.assertEqual(estimate_tokens(""), 0)
        self.assertEqual(estimate_tokens("abcd"), 1)
        self.assertEqual(estimate_tokens("abcde"), 2)

    def test_format_duration(self):
        self.assertEqual(format_duration(900), "0.9s")
        self.assertEqual(format_duration(61000), "1m 1s")


if __name__ == "__main__":
    unittest.main()
