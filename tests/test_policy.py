import tempfile
import unittest
from pathlib import Path

from cofa_orchestrator.policy import (
    PolicyViolation,
    assert_no_external_ai_credentials,
    assert_not_post_submission,
    canonical_model,
    create_post_submission_lock,
)


class PolicyTests(unittest.TestCase):
    def test_allowed_aliases_are_canonicalized(self):
        self.assertEqual(canonical_model("Sol 6.1".replace(" ", "-")), "gpt-6.1-sol")
        self.assertEqual(canonical_model("terra-5.6"), "gpt-5.6-terra")
        self.assertEqual(canonical_model("luna6"), "gpt-6-luna")
        self.assertEqual(canonical_model("sol-6.0"), "gpt-6-sol")

    def test_astra_is_rejected(self):
        with self.assertRaises(PolicyViolation):
            canonical_model("gpt-6-astra")

    def test_external_credentials_are_rejected(self):
        with self.assertRaises(PolicyViolation):
            assert_no_external_ai_credentials({"OPENROUTER_API_KEY": "secret"})

    def test_post_submission_lock_stops_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            create_post_submission_lock(workspace)
            with self.assertRaises(PolicyViolation):
                assert_not_post_submission(workspace)


if __name__ == "__main__":
    unittest.main()

