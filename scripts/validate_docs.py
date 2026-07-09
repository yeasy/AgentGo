#!/usr/bin/env python3
"""Validate the bilingual AgentGo protocol contract using only the stdlib."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 28_672
SEMVER_PATTERN = (
    r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
)
VERSION_RE = re.compile(
    rf"^<!-- AGENTS\.md v(?P<version>{SEMVER_PATTERN}) \| AgentGo \| "
    r"https://github\.com/yeasy/agentgo -->$"
)
H2_PAIRS = (
    ("Purpose", "目的"),
    ("Startup Instructions", "启动指令"),
    ("Trust & Safety", "信任与安全"),
    ("Failure Modes", "失败模式"),
    ("Core Conventions", "核心约定"),
    ("Working Modes", "工作模式"),
    ("Agent Responsibilities", "Agent 职责"),
    ("Review Requests", "审阅请求"),
    ("Self-Evolution Protocol", "自我进化协议"),
    ("Hard Constraints", "硬性约束"),
)
REQUIRED_FAILURE_MODES = frozenset(
    {
        "READ_ONLY",
        "CORRUPT_MEMORY",
        "MISCLASSIFIED_PROJECT",
        "BROKEN_ENV",
        "CONCURRENT_WRITES",
        "UNATTENDED",
        "CONTEXT_LOSS",
    }
)
SEMANTIC_MARKERS = {
    "AGENTS.md": {
        "high-risk in-context confirmation": (
            "require explicit in-context user confirmation",
        ),
        "unattended default decline": (
            "treat every confirmation-gated action as declined",
        ),
        "persistent capability deletion confirmation": (
            "| Delete `rules/`, `workflows/`, `reports/`, `experiments/`, or "
            "`skills/` | Requires confirmation |",
        ),
        "candidate promotion confirmation": (
            "| Promote a candidate from `experiments/` into `rules/`, "
            "`workflows/`, or `skills/` | Requires confirmation |",
        ),
        "secret reads limited to necessity": (
            "Do not read credential files or secret stores unless the current task "
            "requires it",
        ),
        "secret values never echoed": ("never echo secret values",),
        "every adaptation write is audited": (
            "every `.agents/` write appends a changelog entry",
        ),
    },
    "AGENTS.zh-CN.md": {
        "高风险当场确认": ("必须用户当场明确确认",),
        "无人值守默认拒绝": ("把所有需确认的动作一律视为被拒绝",),
        "删除持久能力需确认": (
            "| 删除 `rules/`、`workflows/`、`reports/`、`experiments/` 或 "
            "`skills/` | 需确认 |",
        ),
        "候选促升需确认": (
            "| 从 `experiments/` 把候选促升到 `rules/`、`workflows/` 或 "
            "`skills/` | 需确认 |",
        ),
        "仅在必要时读取 secret": (
            "除非当前任务需要，不读取凭据文件或 secret 存储",
        ),
        "不回显 secret": ("绝不把 secret 真实值回显",),
        "每次适配写入都留审计记录": (
            "每次 `.agents/` 写入都追加一条 changelog",
        ),
    },
}


def extract_version(text: str) -> str | None:
    first_line = text.splitlines()[0] if text.splitlines() else ""
    match = VERSION_RE.fullmatch(first_line)
    return match.group("version") if match else None


def extract_h2(text: str) -> list[str]:
    return re.findall(r"^## (.+)$", text, flags=re.MULTILINE)


def extract_section(text: str, heading: str) -> str:
    match = re.search(
        rf"^## {re.escape(heading)}\n(?P<body>.*?)(?=^## |\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    return match.group("body") if match else ""


def extract_failure_mode_ids(text: str, heading: str) -> set[str]:
    section = extract_section(text, heading)
    return set(
        re.findall(r"^- \*\*([A-Z][A-Z0-9_]*)\*\*[：:]", section, re.MULTILINE)
    )


def validate_semantics(english: str, chinese: str) -> list[str]:
    errors: list[str] = []
    for name, text in (("AGENTS.md", english), ("AGENTS.zh-CN.md", chinese)):
        for contract, markers in SEMANTIC_MARKERS[name].items():
            if not all(marker in text for marker in markers):
                errors.append(f"{name} is missing contract: {contract}")
    return errors


def validate_texts(
    english: str,
    chinese: str,
    *,
    max_bytes: int = MAX_BYTES,
) -> list[str]:
    errors: list[str] = []
    documents = (("AGENTS.md", english), ("AGENTS.zh-CN.md", chinese))

    for name, text in documents:
        size = len(text.encode("utf-8"))
        if size > max_bytes:
            errors.append(f"{name} is {size} bytes; limit is {max_bytes}")

    english_version = extract_version(english)
    chinese_version = extract_version(chinese)
    if english_version is None:
        errors.append("AGENTS.md first line lacks a valid SemVer marker")
    if chinese_version is None:
        errors.append("AGENTS.zh-CN.md first line lacks a valid SemVer marker")
    if english_version is not None and chinese_version is not None:
        if english_version != chinese_version:
            errors.append(
                "version markers differ: "
                f"AGENTS.md={english_version}, AGENTS.zh-CN.md={chinese_version}"
            )

    expected_english_h2 = [pair[0] for pair in H2_PAIRS]
    expected_chinese_h2 = [pair[1] for pair in H2_PAIRS]
    if extract_h2(english) != expected_english_h2:
        errors.append("AGENTS.md H2 names or order differ from the public contract")
    if extract_h2(chinese) != expected_chinese_h2:
        errors.append("AGENTS.zh-CN.md H2 names or order differ from the public contract")

    english_ids = extract_failure_mode_ids(english, H2_PAIRS[3][0])
    chinese_ids = extract_failure_mode_ids(chinese, H2_PAIRS[3][1])
    if english_ids != chinese_ids:
        errors.append(
            "failure-mode IDs differ: "
            f"AGENTS.md={sorted(english_ids)}, AGENTS.zh-CN.md={sorted(chinese_ids)}"
        )
    missing_ids = REQUIRED_FAILURE_MODES - english_ids
    if missing_ids:
        errors.append(f"required failure-mode IDs missing: {sorted(missing_ids)}")

    errors.extend(validate_semantics(english, chinese))
    return errors


def main() -> int:
    english_path = ROOT / "AGENTS.md"
    chinese_path = ROOT / "AGENTS.zh-CN.md"
    english = english_path.read_text(encoding="utf-8")
    chinese = chinese_path.read_text(encoding="utf-8")
    errors = validate_texts(english, chinese)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    version = extract_version(english)
    print(
        "OK: "
        f"AGENTS.md={len(english_path.read_bytes())} bytes, "
        f"AGENTS.zh-CN.md={len(chinese_path.read_bytes())} bytes, "
        f"version=v{version}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
