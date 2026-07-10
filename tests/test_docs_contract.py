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

    def assert_single_mutation_rejected(
        self,
        *,
        filename,
        old,
        new,
        expected_error,
    ):
        baseline_errors = validate_docs.validate_texts(
            self.english,
            self.chinese,
            max_bytes=100_000,
        )
        self.assertNotIn(expected_error, baseline_errors)

        source = self.english if filename == "AGENTS.md" else self.chinese
        self.assertEqual(source.count(old), 1, f"mutation target drifted: {old!r}")
        mutated = source.replace(old, new, 1)
        self.assertNotEqual(mutated, source)

        english = mutated if filename == "AGENTS.md" else self.english
        chinese = mutated if filename == "AGENTS.zh-CN.md" else self.chinese
        errors = validate_docs.validate_texts(
            english,
            chinese,
            max_bytes=100_000,
        )
        self.assertIn(expected_error, errors)

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

    def test_validator_rejects_numeric_prerelease_with_leading_zero(self):
        self.assert_single_mutation_rejected(
            filename="AGENTS.md",
            old="AGENTS.md v1.12.1 |",
            new="AGENTS.md v1.12.1-01 |",
            expected_error="AGENTS.md first line lacks a valid SemVer marker",
        )

    def test_h2_sections_keep_public_mapping_and_order(self):
        english_h2 = validate_docs.extract_h2(self.english)
        chinese_h2 = validate_docs.extract_h2(self.chinese)

        self.assertEqual(english_h2, [pair[0] for pair in validate_docs.H2_PAIRS])
        self.assertEqual(chinese_h2, [pair[1] for pair in validate_docs.H2_PAIRS])

    def test_h3_sections_keep_public_mapping_order_and_parent(self):
        self.assertEqual(
            validate_docs.extract_h3(self.english),
            [pair[0] for pair in validate_docs.H3_PAIRS],
        )
        self.assertEqual(
            validate_docs.extract_h3(self.chinese),
            [pair[1] for pair in validate_docs.H3_PAIRS],
        )

        for english_h2, chinese_h2 in validate_docs.H2_PAIRS:
            expected = validate_docs.H3_PAIRS_BY_H2.get(
                (english_h2, chinese_h2), ()
            )
            with self.subTest(heading=english_h2):
                english_section = validate_docs.extract_section(
                    self.english, english_h2
                )
                self.assertEqual(
                    validate_docs.extract_h3(english_section),
                    [pair[0] for pair in expected],
                )
            with self.subTest(heading=chinese_h2):
                chinese_section = validate_docs.extract_section(
                    self.chinese, chinese_h2
                )
                self.assertEqual(
                    validate_docs.extract_h3(chinese_section),
                    [pair[1] for pair in expected],
                )

    def test_failure_mode_ids_match_fixed_contract_exactly(self):
        english_ids = validate_docs.extract_failure_mode_ids(
            self.english, validate_docs.H2_PAIRS[3][0]
        )
        chinese_ids = validate_docs.extract_failure_mode_ids(
            self.chinese, validate_docs.H2_PAIRS[3][1]
        )

        self.assertEqual(english_ids, chinese_ids)
        self.assertEqual(english_ids, list(validate_docs.FAILURE_MODE_IDS))

    def test_critical_semantics_are_present(self):
        errors = validate_docs.validate_semantics(self.english, self.chinese)
        self.assertEqual(errors, [])

    def test_validator_rejects_removed_h3(self):
        self.assert_single_mutation_rejected(
            filename="AGENTS.md",
            old="### New Projects\n",
            new="",
            expected_error=(
                "AGENTS.md H3 names or order under Working Modes differ from "
                "the public contract"
            ),
        )

    def test_validator_rejects_extra_h3_outside_h2_sections(self):
        self.assert_single_mutation_rejected(
            filename="AGENTS.md",
            old="# AGENTS.md\n",
            new="# AGENTS.md\n\n### Rogue\n",
            expected_error=(
                "AGENTS.md H3 names or order differ from the public contract"
            ),
        )

    def test_validator_ignores_h3_examples_inside_fenced_code(self):
        old = "```\n.agents/\n"
        self.assertEqual(self.english.count(old), 1)
        english = self.english.replace(old, "```\n### Example heading\n.agents/\n", 1)

        errors = validate_docs.validate_texts(
            english,
            self.chinese,
            max_bytes=100_000,
        )
        self.assertEqual(errors, [])

    def test_validator_rejects_marker_relocated_into_fenced_code(self):
        marker = (
            "| Delete `rules/`, `workflows/`, `reports/`, `experiments/`, or "
            "`skills/` | Requires confirmation |"
        )
        self.assert_single_mutation_rejected(
            filename="AGENTS.md",
            old=marker,
            new=(
                "| Delete persistent capability files | Free | No confirmation. |"
                f"\n\n```text\n{marker}\n```"
            ),
            expected_error=(
                "AGENTS.md is missing contract: persistent capability deletion "
                "confirmation"
            ),
        )

    def test_validator_rejects_marker_in_blockquote_fenced_code(self):
        marker = (
            "| Delete `rules/`, `workflows/`, `reports/`, `experiments/`, or "
            "`skills/` | Requires confirmation |"
        )
        self.assert_single_mutation_rejected(
            filename="AGENTS.md",
            old=marker,
            new=(
                "| Delete persistent capability files | Free | No confirmation. |"
                f"\n\n> ```text\n> {marker}\n> ```"
            ),
            expected_error=(
                "AGENTS.md is missing contract: persistent capability deletion "
                "confirmation"
            ),
        )

    def test_validator_rejects_marker_in_indented_code(self):
        marker = (
            "| Delete `rules/`, `workflows/`, `reports/`, `experiments/`, or "
            "`skills/` | Requires confirmation |"
        )
        for indentation in ("    ", "\t", " \t"):
            with self.subTest(indentation=repr(indentation)):
                self.assert_single_mutation_rejected(
                    filename="AGENTS.md",
                    old=marker,
                    new=(
                        "| Delete persistent capability files | Free | "
                        f"No confirmation. |\n\n{indentation}{marker}"
                    ),
                    expected_error=(
                        "AGENTS.md is missing contract: persistent capability "
                        "deletion confirmation"
                    ),
                )

    def test_validator_rejects_h3_moved_under_wrong_parent(self):
        self.assert_single_mutation_rejected(
            filename="AGENTS.md",
            old="### Existing Projects\n\nUnderstand progressively;",
            new=(
                "## Agent Responsibilities\n\n### Existing Projects\n\n"
                "Understand progressively;"
            ),
            expected_error=(
                "AGENTS.md H3 names or order under Working Modes differ from "
                "the public contract"
            ),
        )

    def test_validator_rejects_extra_failure_mode(self):
        actual_ids = ["EXTRA_MODE", *validate_docs.FAILURE_MODE_IDS]
        expected_error = (
            "AGENTS.md failure-mode IDs differ from the fixed contract: "
            f"expected={list(validate_docs.FAILURE_MODE_IDS)}, "
            f"actual={actual_ids}"
        )
        self.assert_single_mutation_rejected(
            filename="AGENTS.md",
            old="- **READ_ONLY**:",
            new="- **EXTRA_MODE**: Synthetic mode.\n- **READ_ONLY**:",
            expected_error=expected_error,
        )

    def test_validator_rejects_duplicate_failure_mode(self):
        read_only_entry = next(
            line
            for line in self.english.splitlines()
            if line.startswith("- **READ_ONLY**:")
        )
        self.assertEqual(self.english.count(read_only_entry), 1)
        english = self.english.replace(
            read_only_entry,
            f"{read_only_entry}\n{read_only_entry}",
            1,
        )

        errors = validate_docs.validate_texts(
            english,
            self.chinese,
            max_bytes=100_000,
        )
        self.assertTrue(
            any(
                error.startswith(
                    "AGENTS.md failure-mode IDs differ from the fixed contract"
                )
                for error in errors
            ),
            errors,
        )

    def test_validator_rejects_failure_mode_moved_into_fenced_code(self):
        read_only_entry = next(
            line
            for line in self.english.splitlines()
            if line.startswith("- **READ_ONLY**:")
        )
        self.assertEqual(self.english.count(read_only_entry), 1)
        english = self.english.replace(
            read_only_entry,
            f"```text\n{read_only_entry}\n```",
            1,
        )
        self.assertEqual(english.count("READ_ONLY"), self.english.count("READ_ONLY"))

        errors = validate_docs.validate_texts(
            english,
            self.chinese,
            max_bytes=100_000,
        )
        self.assertTrue(
            any(
                error.startswith(
                    "AGENTS.md failure-mode IDs differ from the fixed contract"
                )
                for error in errors
            ),
            errors,
        )

    def test_validator_rejects_weakened_current_message_priority(self):
        self.assert_single_mutation_rejected(
            filename="AGENTS.md",
            old="The current message outranks every `AGENTS.md`",
            new="A prior message may outrank an `AGENTS.md`",
            expected_error=(
                "AGENTS.md is missing contract: current-message priority and "
                "closest instruction scope"
            ),
        )

    def test_validator_rejects_weakened_closest_non_vendored_scope(self):
        self.assert_single_mutation_rejected(
            filename="AGENTS.zh-CN.md",
            old="离目标产物最近且非依赖/生成目录内的 `AGENTS.md` 生效",
            new="任意目录内的 `AGENTS.md` 都可生效",
            expected_error=(
                "AGENTS.zh-CN.md is missing contract: 当前消息优先与最近指令范围"
            ),
        )

    def test_validator_rejects_running_only_network_code_rule(self):
        self.assert_single_mutation_rejected(
            filename="AGENTS.md",
            old="installing or running network-fetched code",
            new="running network-fetched code",
            expected_error=(
                "AGENTS.md is missing contract: network-fetched code installation "
                "requires confirmation"
            ),
        )

    def test_validator_rejects_negated_network_code_confirmation(self):
        self.assert_single_mutation_rejected(
            filename="AGENTS.md",
            old="—require explicit in-context user confirmation.",
            new="—do not require explicit in-context user confirmation.",
            expected_error=(
                "AGENTS.md is missing contract: network-fetched code installation "
                "requires confirmation"
            ),
        )

    def test_validator_rejects_incomplete_misclassified_project_triggers(self):
        self.assert_single_mutation_rejected(
            filename="AGENTS.zh-CN.md",
            old="项目类型、入口或验证命令不确定或受到质疑",
            new="项目类型不确定或受到质疑",
            expected_error=(
                "AGENTS.zh-CN.md is missing contract: 项目误分类三类触发面"
            ),
        )

    def test_validator_rejects_promotion_threshold_change_from_three_to_four(self):
        self.assert_single_mutation_rejected(
            filename="AGENTS.md",
            old="at least 3 distinct tasks",
            new="at least 4 distinct tasks",
            expected_error=(
                "AGENTS.md is missing contract: capability promotion thresholds"
            ),
        )

    def test_validator_rejects_promotion_last_five_window_change(self):
        self.assert_single_mutation_rejected(
            filename="AGENTS.zh-CN.md",
            old="最近 5 次记录",
            new="最近 6 次记录",
            expected_error="AGENTS.zh-CN.md is missing contract: 能力促升阈值",
        )

    def test_validator_rejects_demotion_two_of_last_five_change(self):
        self.assert_single_mutation_rejected(
            filename="AGENTS.md",
            old="at least 2 of the last 5 uses",
            new="at least 3 of the last 5 uses",
            expected_error=(
                "AGENTS.md is missing contract: capability demotion thresholds"
            ),
        )

    def test_validator_rejects_demotion_ninety_day_change(self):
        self.assert_single_mutation_rejected(
            filename="AGENTS.zh-CN.md",
            old="90 天无使用记录",
            new="60 天无使用记录",
            expected_error="AGENTS.zh-CN.md is missing contract: 能力降级阈值",
        )

    def test_validator_rejects_missing_required_directory(self):
        self.assert_single_mutation_rejected(
            filename="AGENTS.zh-CN.md",
            old="│   ├── review-findings.md\n",
            new="",
            expected_error="AGENTS.zh-CN.md is missing contract: 适配层必需目录",
        )

    def test_validator_rejects_template_without_same_language_requirement(self):
        self.assert_single_mutation_rejected(
            filename="AGENTS.zh-CN.md",
            old="官方同语言模板",
            new="官方模板",
            expected_error=(
                "AGENTS.zh-CN.md is missing contract: 模板仅用官方同语言来源"
            ),
        )

    def test_validator_rejects_missing_official_template_source(self):
        self.assert_single_mutation_rejected(
            filename="AGENTS.md",
            old="official AgentGo repository only—",
            new="AgentGo repository—",
            expected_error=(
                "AGENTS.md is missing contract: template official same-language "
                "source"
            ),
        )

    def test_validator_rejects_template_reconstruction_after_fetch_failure(self):
        self.assert_single_mutation_rejected(
            filename="AGENTS.zh-CN.md",
            old="失败/无网络则停止；不得凭记忆重建或部分更新。",
            new="失败/无网络时可凭记忆重建。",
            expected_error=(
                "AGENTS.zh-CN.md is missing contract: 模板获取失败不得凭记忆重建"
            ),
        )

    def test_validator_rejects_template_main_over_release_tag(self):
        self.assert_single_mutation_rejected(
            filename="AGENTS.md",
            old="prefer the latest release tag over `main`",
            new="prefer `main` over the latest release tag",
            expected_error=(
                "AGENTS.md is missing contract: template release tag preference"
            ),
        )

    def test_validator_rejects_missing_sensitive_section_confirmation(self):
        self.assert_single_mutation_rejected(
            filename="AGENTS.zh-CN.md",
            old="信任与安全、进化规则或硬性约束有变化仍需用户明确确认",
            new="普通文字变化仍需用户明确确认",
            expected_error=(
                "AGENTS.zh-CN.md is missing contract: 模板敏感章节变化需确认"
            ),
        )

    def test_validator_rejects_maintenance_threshold_change_from_200_to_201(self):
        self.assert_single_mutation_rejected(
            filename="AGENTS.md",
            old="any `memory/` file exceeds 200 lines",
            new="any `memory/` file exceeds 201 lines",
            expected_error=(
                "AGENTS.md is missing contract: maintenance size and cadence "
                "thresholds"
            ),
        )

    def test_validator_rejects_maintenance_aggregate_threshold_change(self):
        self.assert_single_mutation_rejected(
            filename="AGENTS.zh-CN.md",
            old="`memory/` 总计约超过 3,000 行",
            new="`memory/` 总计约超过 4,000 行",
            expected_error=(
                "AGENTS.zh-CN.md is missing contract: 维护规模与频率阈值"
            ),
        )

    def test_validator_rejects_maintenance_changelog_threshold_change(self):
        self.assert_single_mutation_rejected(
            filename="AGENTS.md",
            old="changelog gains at least 30 lines since maintenance",
            new="changelog gains at least 31 lines since maintenance",
            expected_error=(
                "AGENTS.md is missing contract: maintenance size and cadence "
                "thresholds"
            ),
        )

    def test_validator_rejects_unprotected_tmp_sessions(self):
        self.assert_single_mutation_rejected(
            filename="AGENTS.zh-CN.md",
            old="未协调的 `tmp/sessions/<session-id>/` 必须先合并或归档",
            new="`tmp/sessions/<session-id>/` 可直接删除",
            expected_error=(
                "AGENTS.zh-CN.md is missing contract: 维护保护 pinned 与会话草稿"
            ),
        )

    def test_validator_rejects_unprotected_pinned_entries(self):
        self.assert_single_mutation_rejected(
            filename="AGENTS.md",
            old=(
                "Never prune/merge/archive `status=pinned` or legacy "
                "`<!-- pinned -->` entries."
            ),
            new="Pinned entries may be pruned.",
            expected_error=(
                "AGENTS.md is missing contract: maintenance pinned and session "
                "protection"
            ),
        )

    def test_validator_rejects_changed_normal_changelog_format(self):
        old = (
            "Normal: `YYYY-MM-DD | <create|update|delete|merge|rename> | "
            "<path or artifact> | <what was done>`."
        )
        self.assert_single_mutation_rejected(
            filename="AGENTS.md",
            old=old,
            new=old.replace("<what was done>", "<summary>"),
            expected_error="AGENTS.md is missing contract: normal changelog format",
        )

    def test_validator_rejects_missing_extended_changelog_trigger(self):
        self.assert_single_mutation_rejected(
            filename="AGENTS.zh-CN.md",
            old="删除、合并、`[MAINTENANCE]`、bootstrap 或重扫：",
            new="删除、合并或 `[MAINTENANCE]`：",
            expected_error=(
                "AGENTS.zh-CN.md is missing contract: 扩展 changelog 格式与触发条件"
            ),
        )

    def test_validator_rejects_changed_extended_changelog_format(self):
        self.assert_single_mutation_rejected(
            filename="AGENTS.md",
            old=(
                "`YYYY-MM-DDTHH:MM:SSZ | <agent>:<session> | <op|event> | "
                "<path or artifact> | <what> | <why>`"
            ),
            new=(
                "`YYYY-MM-DD | <agent> | <op|event> | <path or artifact> | "
                "<what>`"
            ),
            expected_error=(
                "AGENTS.md is missing contract: extended changelog format and "
                "triggers"
            ),
        )

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
