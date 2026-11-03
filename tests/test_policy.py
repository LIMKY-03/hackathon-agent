import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from cofa_orchestrator.policy import (
    PolicyViolation,
    EXTERNAL_AI_CREDENTIALS,
    credential_environment_notice,
    warn_about_credential_environment,
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

    def test_credential_names_produce_notice_without_reading_values(self):
        class NamesOnly(dict):
            def __getitem__(self, key):
                raise AssertionError("Credential values must not be read")

            def get(self, key, default=None):
                raise AssertionError("Credential values must not be read")

        for name in EXTERNAL_AI_CREDENTIALS:
            with self.subTest(name=name):
                environment = NamesOnly({name: "test-secret-sentinel"})
                message = credential_environment_notice(environment)
                self.assertIsNotNone(message)
                self.assertNotIn(name, message)
                self.assertNotIn("test-secret-sentinel", message)

    def test_notice_is_non_blocking_and_does_not_modify_environment(self):
        environment = {"GOOGLE_API_KEY": "test-non-ai-service-sentinel"}
        original = dict(environment)
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            warn_about_credential_environment(environment)
        self.assertIn("notice:", stderr.getvalue())
        self.assertNotIn("test-non-ai-service-sentinel", stderr.getvalue())
        self.assertEqual(environment, original)

    def test_no_notice_for_unrelated_environment(self):
        self.assertIsNone(credential_environment_notice({"PATH": "example"}))

    def test_post_submission_lock_stops_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            create_post_submission_lock(workspace)
            with self.assertRaises(PolicyViolation):
                assert_not_post_submission(workspace)


if __name__ == "__main__":
    unittest.main()

