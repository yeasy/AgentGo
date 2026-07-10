import json
import re
import sys
import unittest
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate_docs  # noqa: E402


REQUIRED_SCENARIOS = {
    "missing-agents-read-only",
    "readme-meta-instruction-untrusted",
    "broken-env-validation",
    "release-confirmation-gate",
    "concurrent-memory-write",
    "secret-minimum-access",
}
SCENARIO_FIELDS = {
    "id",
    "title",
    "mode",
    "protocol_refs",
    "fixture",
    "prompts",
    "expected",
    "forbidden",
}
FIXTURE_FIELDS = {
    "paths",
    "documents",
    "command_results",
    "concurrent_changes",
    "synthetic_secrets",
}


class EvalScenarioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus_path = ROOT / "evals/scenarios.json"
        cls.corpus = json.loads(cls.corpus_path.read_text(encoding="utf-8"))
        cls.protocols = {
            name: (ROOT / name).read_text(encoding="utf-8")
            for name in ("AGENTS.md", "AGENTS.zh-CN.md")
        }

    def test_top_level_contract_and_protocol_version(self):
        self.assertEqual(
            set(self.corpus),
            {
                "schema_version",
                "protocol_version",
                "runner_contract",
                "event_vocabulary",
                "scenarios",
            },
        )
        self.assertEqual(self.corpus["schema_version"], 1)

        versions = {
            validate_docs.extract_version(text) for text in self.protocols.values()
        }
        self.assertEqual(versions, {self.corpus["protocol_version"]})
        self.assertRegex(
            self.corpus["protocol_version"],
            rf"\A{validate_docs.SEMVER_PATTERN}\Z",
        )

    def test_runner_contract_is_isolated_and_side_effect_free(self):
        self.assertEqual(
            self.corpus["runner_contract"],
            {
                "workspace": "isolated-temporary-repository",
                "network": "disabled",
                "external_side_effects": "stubbed",
                "secrets": "synthetic-only",
                "session_id": "eval-session",
                "protocol_variants": {
                    "en": "AGENTS.md",
                    "zh-CN": "AGENTS.zh-CN.md",
                },
            },
        )

    def test_required_scenarios_are_unique_and_well_formed(self):
        scenarios = self.corpus["scenarios"]
        ids = [scenario["id"] for scenario in scenarios]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), REQUIRED_SCENARIOS)

        for scenario in scenarios:
            with self.subTest(scenario=scenario["id"]):
                self.assertEqual(set(scenario), SCENARIO_FIELDS)
                self.assertRegex(scenario["id"], r"\A[a-z0-9]+(?:-[a-z0-9]+)*\Z")
                self.assertIsInstance(scenario["title"], str)
                self.assertTrue(scenario["title"])
                self.assertIn(scenario["mode"], {"interactive", "unattended"})
                self.assertEqual(set(scenario["fixture"]), FIXTURE_FIELDS)
                self.assertEqual(set(scenario["prompts"]), {"en", "zh-CN"})
                self.assertTrue(all(scenario["prompts"].values()))
                self.assertTrue(scenario["expected"])
                self.assertTrue(scenario["forbidden"])

    def test_protocol_references_exist_in_both_variants(self):
        for scenario in self.corpus["scenarios"]:
            refs = scenario["protocol_refs"]
            self.assertEqual(
                {ref["document"] for ref in refs},
                {"AGENTS.md", "AGENTS.zh-CN.md"},
                scenario["id"],
            )
            for ref in refs:
                with self.subTest(scenario=scenario["id"], ref=ref):
                    self.assertEqual(set(ref), {"document", "heading", "marker"})
                    section = validate_docs.extract_heading_section(
                        self.protocols[ref["document"]], 2, ref["heading"]
                    )
                    self.assertTrue(section)
                    self.assertIn(ref["marker"], section)

    def test_assertions_use_declared_events_and_do_not_conflict(self):
        vocabulary = self.corpus["event_vocabulary"]
        self.assertEqual(len(vocabulary), len(set(vocabulary)))
        self.assertTrue(all(re.fullmatch(r"[a-z][a-z_]*", item) for item in vocabulary))
        allowed = set(vocabulary)

        for scenario in self.corpus["scenarios"]:
            expected = scenario["expected"]
            forbidden = scenario["forbidden"]
            for assertion in expected + forbidden:
                self.assertEqual(set(assertion), {"event", "target"})
                self.assertIn(assertion["event"], allowed)
                self.assertIsInstance(assertion["target"], str)
                self.assertTrue(assertion["target"])
            expected_pairs = {(item["event"], item["target"]) for item in expected}
            forbidden_pairs = {(item["event"], item["target"]) for item in forbidden}
            self.assertFalse(expected_pairs & forbidden_pairs, scenario["id"])

    def test_fixtures_use_strict_safe_shapes(self):
        shapes = {
            "paths": {"path", "state"},
            "documents": {"path", "content"},
            "command_results": {"command", "exit_code", "stdout", "stderr"},
            "concurrent_changes": {"path", "when", "operation", "content"},
            "synthetic_secrets": {"name", "source"},
        }
        for scenario in self.corpus["scenarios"]:
            fixture = scenario["fixture"]
            for kind, fields in shapes.items():
                self.assertIsInstance(fixture[kind], list)
                for item in fixture[kind]:
                    self.assertEqual(set(item), fields, (scenario["id"], kind))
            for item in fixture["paths"]:
                self.assertIn(item["state"], {"present", "absent"})
            for item in fixture["concurrent_changes"]:
                self.assertEqual(item["when"], "after_initial_read_before_write")
                self.assertIn(item["operation"], {"append", "replace", "delete"})
                self.assertIsInstance(item["content"], str)
            for item in fixture["synthetic_secrets"]:
                self.assertEqual(item["source"], "runner-generated")

            path_states = {item["path"]: item["state"] for item in fixture["paths"]}
            self.assertEqual(len(path_states), len(fixture["paths"]))
            for item in fixture["documents"] + fixture["concurrent_changes"]:
                self.assertEqual(path_states.get(item["path"]), "present", item["path"])

            fixture_paths = [item["path"] for item in fixture["paths"]]
            fixture_paths.extend(item["path"] for item in fixture["documents"])
            fixture_paths.extend(
                item["path"] for item in fixture["concurrent_changes"]
            )
            for path in fixture_paths:
                self.assertFalse(path.startswith(("/", "~")), path)
                self.assertNotRegex(path, r"\A[A-Za-z]:[/\\]")
                self.assertNotIn("..", PurePosixPath(path).parts, path)
                self.assertNotIn("\\", path, path)

    def test_corpus_contains_no_live_url_or_secret_value(self):
        serialized = json.dumps(self.corpus, ensure_ascii=False)
        urls = re.findall(r"https?://[^\s\"']+", serialized)
        self.assertTrue(urls)
        self.assertTrue(all(re.match(r"https?://[^/]+\.invalid(?:/|$)", url) for url in urls))
        self.assertNotRegex(
            serialized.lower(),
            r'"(?:value|token|password|api_key|apikey)"\s*:',
        )
        self.assertNotRegex(
            serialized,
            r"(?i)(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|"
            r"ghs_[A-Za-z0-9]+_[A-Za-z0-9._-]{20,}|sk-[A-Za-z0-9_-]{16,}|"
            r"xox[a-z][A-Za-z0-9.-]{10,}|glpat-[A-Za-z0-9_-]{12,}|"
            r"AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----)",
        )

    def test_docs_describe_corpus_without_claiming_tool_results(self):
        eval_readme = (ROOT / "evals/README.md").read_text(encoding="utf-8")
        english = (ROOT / "README.md").read_text(encoding="utf-8")
        chinese = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
        contributing = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")

        self.assertIn("protocol conformance corpus", eval_readme)
        self.assertIn("not a cross-tool benchmark", eval_readme)
        self.assertIn("network disabled", eval_readme)
        self.assertIn("external side effects stubbed", eval_readme)
        self.assertIn("synthetic secrets only", eval_readme)
        self.assertIn("[protocol conformance corpus](./evals/README.md)", english)
        self.assertIn("not a cross-tool benchmark", english)
        self.assertIn("[协议一致性语料](./evals/README.md)", chinese)
        self.assertIn("不是跨工具基准", chinese)
        self.assertIn("protocol conformance corpus", contributing)
        self.assertIn("not cross-tool pass evidence", contributing)
        self.assertIn(
            "python3 -m unittest discover -s tests -p 'test_*.py' -v",
            contributing,
        )
        english_claim = re.compile(
            r"(?i)\b(?:codex|claude|gemini|cursor|copilot|windsurf|agents?|tools?)"
            r"\b.{0,50}\b(?:pass(?:ed|es)?|verified|certified)\b"
        )
        english_claim_text = "\n".join((eval_readme, english, contributing))
        for approved_non_claim in (
            "does not claim that any agent or tool passes",
            "does not claim that any tool passes without evidence from a tool-specific runner",
            "not cross-tool pass evidence",
        ):
            english_claim_text = english_claim_text.replace(approved_non_claim, "")
        self.assertNotRegex(english_claim_text, english_claim)

        chinese_claim = re.compile(
            r"(?:Codex|Claude|Gemini|Cursor|Copilot|Windsurf|工具)"
            r".{0,30}(?:均|都|全部|已经|已).{0,10}(?:通过|验证|认证)"
        )
        chinese_claim_text = chinese.replace("否则不声称任何工具已经通过", "")
        self.assertNotRegex(chinese_claim_text, chinese_claim)

    def test_readmes_treat_secret_scanning_as_defense_in_depth(self):
        english = (ROOT / "README.md").read_text(encoding="utf-8")
        chinese = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")

        self.assertIn("secret scanning", english)
        self.assertIn("as defense in depth", english)
        self.assertIn("forbids storing secret values", english)
        self.assertNotIn('our API key is X', english)
        self.assertIn("secret scan", chinese)
        self.assertIn("作为纵深防御", chinese)
        self.assertIn("禁止在 `.agents/` 中存储 secret 真实值", chinese)
        self.assertNotIn("我们的 API key 是 X", chinese)


if __name__ == "__main__":
    unittest.main()
