import importlib.util
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_docs", ROOT / "scripts" / "validate_docs.py"
)
validate_docs = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(validate_docs)


class DocsContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.english_path = ROOT / "AGENTS.md"
        cls.chinese_path = ROOT / "AGENTS.zh-CN.md"
        cls.english = cls.english_path.read_text(encoding="utf-8")
        cls.chinese = cls.chinese_path.read_text(encoding="utf-8")

    def test_documents_fit_context_budget(self):
        for path in (self.english_path, self.chinese_path):
            with self.subTest(path=path.name):
                self.assertLessEqual(
                    len(path.read_bytes()),
                    validate_docs.MAX_BYTES,
                    f"{path.name} exceeds {validate_docs.MAX_BYTES} bytes",
                )

    def test_first_line_versions_match_semver(self):
        english_version = validate_docs.extract_version(self.english)
        chinese_version = validate_docs.extract_version(self.chinese)

        self.assertIsNotNone(english_version)
        self.assertEqual(english_version, chinese_version)
        self.assertRegex(english_version, re.compile(validate_docs.SEMVER_PATTERN))

    def test_h2_sections_keep_public_mapping_and_order(self):
        english_h2 = validate_docs.extract_h2(self.english)
        chinese_h2 = validate_docs.extract_h2(self.chinese)

        self.assertEqual(english_h2, [pair[0] for pair in validate_docs.H2_PAIRS])
        self.assertEqual(chinese_h2, [pair[1] for pair in validate_docs.H2_PAIRS])

    def test_failure_mode_ids_match_and_include_required_modes(self):
        english_ids = validate_docs.extract_failure_mode_ids(
            self.english, validate_docs.H2_PAIRS[3][0]
        )
        chinese_ids = validate_docs.extract_failure_mode_ids(
            self.chinese, validate_docs.H2_PAIRS[3][1]
        )

        self.assertEqual(english_ids, chinese_ids)
        self.assertTrue(validate_docs.REQUIRED_FAILURE_MODES <= english_ids)

    def test_critical_semantics_are_present(self):
        errors = validate_docs.validate_semantics(self.english, self.chinese)
        self.assertEqual(errors, [])

    def test_validator_does_not_require_equal_physical_line_counts(self):
        chinese_with_extra_blank_line = self.chinese + "\n"
        self.assertNotEqual(
            len(self.english.splitlines()),
            len(chinese_with_extra_blank_line.splitlines()),
        )

        errors = validate_docs.validate_texts(
            self.english,
            chinese_with_extra_blank_line,
            max_bytes=100_000,
        )
        self.assertEqual(errors, [])

    def test_readme_stable_examples_match_protocol_version(self):
        version = validate_docs.extract_version(self.english)
        expected = {
            "README.md": (
                f"release tag such as `v{version}`",
                f"agentgo/v{version}/AGENTS.md",
                f"AGENTS.md v{version}",
            ),
            "README.zh-CN.md": (
                f"release tag，例如 `v{version}`",
                f"agentgo/v{version}/AGENTS.zh-CN.md",
                f"AGENTS.md v{version}",
            ),
        }

        for name, markers in expected.items():
            text = (ROOT / name).read_text(encoding="utf-8")
            with self.subTest(path=name):
                self.assertTrue(all(marker in text for marker in markers))

    def test_contributing_sync_contract_avoids_physical_line_promises(self):
        text = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")

        self.assertNotIn("same line count", text)
        self.assertNotIn("headings on the same line numbers", text)
        self.assertIn("version markers", text)
        self.assertIn("section structure", text)
        self.assertIn("critical protocol contracts", text)


if __name__ == "__main__":
    unittest.main()
