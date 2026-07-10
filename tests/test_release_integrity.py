import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate_docs  # noqa: E402


class ReleaseIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = (ROOT / ".github/workflows/docs.yml").read_text(
            encoding="utf-8"
        )
        cls.english = (ROOT / "README.md").read_text(encoding="utf-8")
        cls.chinese = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
        cls.version = validate_docs.extract_version(
            (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        )

    def test_external_actions_are_full_sha_pinned_with_version_comments(self):
        uses_lines = re.findall(
            r"^\s*-\s+uses:\s+(?P<target>\S+?)(?:\s+#\s+(?P<version>\S+))?\s*$",
            self.workflow,
            re.MULTILINE,
        )
        self.assertTrue(uses_lines, "workflow must use at least one action")

        for target, version in uses_lines:
            if target.startswith("./"):
                continue
            action, separator, ref = target.rpartition("@")
            self.assertTrue(separator and "/" in action, target)
            self.assertRegex(ref, r"\A[0-9a-f]{40}\Z", target)
            self.assertRegex(version, rf"\Av{validate_docs.SEMVER_PATTERN}\Z", target)

    def test_workflow_uses_read_only_permissions_and_release_event(self):
        pre_jobs = self.workflow.split("\njobs:\n", 1)[0]
        self.assertRegex(pre_jobs, r"(?m)^permissions:\n  contents: read$")
        self.assertRegex(
            pre_jobs,
            r"(?m)^  release:\n    types: \[published\]$",
        )

    def test_release_job_validates_tag_and_public_templates(self):
        self.assertIn("release-integrity:", self.workflow)
        self.assertIn("github.event.release.tag_name", self.workflow)
        self.assertIn("ref: ${{ env.RELEASE_TAG }}", self.workflow)
        self.assertIn("persist-credentials: false", self.workflow)
        self.assertIn("python3 scripts/validate_docs.py", self.workflow)
        self.assertIn(
            "raw.githubusercontent.com/yeasy/agentgo/${RELEASE_TAG}/AGENTS.md",
            self.workflow,
        )
        self.assertIn(
            "raw.githubusercontent.com/yeasy/agentgo/${RELEASE_TAG}/AGENTS.zh-CN.md",
            self.workflow,
        )
        self.assertGreaterEqual(self.workflow.count("cmp "), 2)

    def test_ci_runs_contract_suite_not_physical_parity_checks(self):
        self.assertIn(
            "python3 -m unittest discover -s tests -p 'test_*.py' -v",
            self.workflow,
        )
        self.assertNotIn("wc -l", self.workflow)
        self.assertNotIn("grep -n '^#'", self.workflow)

    def test_link_check_does_not_hide_security_reporting(self):
        self.assertNotIn("github\\.com/yeasy/AgentGo/security", self.workflow)

    def test_dependabot_tracks_github_actions_weekly(self):
        dependabot = (ROOT / ".github/dependabot.yml").read_text(encoding="utf-8")
        self.assertRegex(dependabot, r'(?m)^version: 2$')
        self.assertRegex(
            dependabot,
            r'(?m)^  - package-ecosystem: "github-actions"$',
        )
        self.assertRegex(dependabot, r'(?m)^    directory: "/"$')
        self.assertRegex(dependabot, r'(?m)^      interval: "weekly"$')

    def test_python_cache_artifacts_are_ignored(self):
        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertRegex(gitignore, r"(?m)^__pycache__/$")
        self.assertRegex(gitignore, r"(?m)^\*\.py\[cod\]$")

    def test_default_template_downloads_are_release_pinned(self):
        expected_ref = f"v{self.version}"
        for name, readme in (
            ("README.md", self.english),
            ("README.zh-CN.md", self.chinese),
        ):
            refs = re.findall(
                r"https://raw\.githubusercontent\.com/yeasy/agentgo/"
                r"([^/]+)/AGENTS(?:\.zh-CN)?\.md",
                readme,
            )
            self.assertTrue(refs, name)
            self.assertEqual({expected_ref}, set(refs), name)

        self.assertIn("unreleased edge channel", self.english)
        self.assertIn("未发布的 edge 通道", self.chinese)


if __name__ == "__main__":
    unittest.main()
