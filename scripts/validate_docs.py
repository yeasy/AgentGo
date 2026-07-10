#!/usr/bin/env python3
"""Validate the bilingual AgentGo protocol contract using only the stdlib."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 28_672
NUMERIC_IDENTIFIER = r"(?:0|[1-9]\d*)"
NON_NUMERIC_IDENTIFIER = r"(?:\d*[A-Za-z-][0-9A-Za-z-]*)"
PRERELEASE_IDENTIFIER = (
    rf"(?:{NUMERIC_IDENTIFIER}|{NON_NUMERIC_IDENTIFIER})"
)
BUILD_IDENTIFIER = r"[0-9A-Za-z-]+"
SEMVER_PATTERN = (
    rf"{NUMERIC_IDENTIFIER}\.{NUMERIC_IDENTIFIER}\.{NUMERIC_IDENTIFIER}"
    rf"(?:-{PRERELEASE_IDENTIFIER}"
    rf"(?:\.{PRERELEASE_IDENTIFIER})*)?"
    rf"(?:\+{BUILD_IDENTIFIER}(?:\.{BUILD_IDENTIFIER})*)?"
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
H3_PAIRS = (
    ("New Projects", "新项目"),
    ("Existing Projects", "已有项目"),
    ("Evolution Model", "进化模型"),
    ("Proactive Suggestion Gate", "主动建议门控"),
    ("Directory Layout", "目录结构"),
    ("Evolution Rules", "进化规则"),
    ("Updating This Template", "更新本模板"),
    ("When to Record", "何时记录"),
    ("Maintenance Cadence", "维护节奏"),
    ("Changelog Format", "Changelog 格式"),
)
H3_PAIRS_BY_H2 = {
    H2_PAIRS[5]: H3_PAIRS[:2],
    H2_PAIRS[8]: H3_PAIRS[2:],
}
FAILURE_MODE_IDS = (
    "READ_ONLY",
    "CORRUPT_MEMORY",
    "MISCLASSIFIED_PROJECT",
    "BROKEN_ENV",
    "CONCURRENT_WRITES",
    "UNATTENDED",
    "CONTEXT_LOSS",
)
FENCED_MARKER_CONTRACTS = frozenset(
    {
        ("AGENTS.md", "required adaptation directories"),
        ("AGENTS.zh-CN.md", "适配层必需目录"),
    }
)
SEMANTIC_MARKERS = {
    "AGENTS.md": {
        "current-message priority and closest instruction scope": (
            2,
            "Trust & Safety",
            (
                "The current message outranks every `AGENTS.md`",
                "the closest non-vendored `AGENTS.md` governs an artifact",
            ),
        ),
        "network-fetched code installation requires confirmation": (
            2,
            "Trust & Safety",
            (
                "installing or running network-fetched code",
                "require explicit in-context user confirmation",
            ),
        ),
        "misclassified-project trigger surfaces": (
            2,
            "Failure Modes",
            (
                "project type, entry points, or validation commands are uncertain "
                "or challenged",
            ),
        ),
        "unattended default decline": (
            2,
            "Failure Modes",
            ("treat every confirmation-gated action as declined",),
        ),
        "capability promotion thresholds": (
            3,
            "Evolution Model",
            ("at least 3 distinct tasks", "last 5 recorded uses"),
        ),
        "capability demotion thresholds": (
            3,
            "Evolution Model",
            ("at least 2 of the last 5 uses", "90 days"),
        ),
        "required adaptation directories": (
            3,
            "Directory Layout",
            (
                "project-overview.md",
                "source-index.md",
                "review-findings.md",
                "open-items.md",
                "outcomes.md",
                "secret-requirements.md",
                "├── rules/",
                "├── workflows/",
                "├── reports/",
                "├── experiments/",
                "├── tmp/",
                "├── skills/",
                "├── archive/",
                "└── changelog.md",
            ),
        ),
        "persistent capability deletion confirmation": (
            3,
            "Evolution Rules",
            (
                "| Delete `rules/`, `workflows/`, `reports/`, `experiments/`, or "
                "`skills/` | Requires confirmation |",
            ),
        ),
        "candidate promotion confirmation": (
            3,
            "Evolution Rules",
            (
                "| Promote a candidate from `experiments/` into `rules/`, "
                "`workflows/`, or `skills/` | Requires confirmation |",
            ),
        ),
        "template official same-language source": (
            3,
            "Updating This Template",
            ("official same-language template", "official AgentGo repository only"),
        ),
        "template fetch failure stops without reconstruction": (
            3,
            "Updating This Template",
            (
                "On failure/no network, stop; never reconstruct from memory or apply "
                "a partial update.",
            ),
        ),
        "template release tag preference": (
            3,
            "Updating This Template",
            ("prefer the latest release tag over `main`",),
        ),
        "template sensitive-section confirmation": (
            3,
            "Updating This Template",
            (
                "Changes to Trust & Safety, Evolution Rules, or Hard Constraints "
                "require explicit confirmation even without conflict.",
            ),
        ),
        "maintenance size and cadence thresholds": (
            3,
            "Maintenance Cadence",
            (
                "any `memory/` file exceeds 200 lines",
                "aggregate `memory/` exceeds about 3,000 lines",
                "changelog gains at least 30 lines since maintenance",
            ),
        ),
        "maintenance pinned and session protection": (
            3,
            "Maintenance Cadence",
            (
                "except unreconciled `tmp/sessions/<session-id>/`",
                "Never prune/merge/archive `status=pinned` or legacy "
                "`<!-- pinned -->` entries.",
            ),
        ),
        "normal changelog format": (
            3,
            "Changelog Format",
            (
                "Normal: `YYYY-MM-DD | <create|update|delete|merge|rename> | "
                "<path or artifact> | <what was done>`.",
            ),
        ),
        "extended changelog format and triggers": (
            3,
            "Changelog Format",
            (
                "For delete, merge, `[MAINTENANCE]`, bootstrap, or rescan:",
                "`YYYY-MM-DDTHH:MM:SSZ | <agent>:<session> | <op|event> | "
                "<path or artifact> | <what> | <why>`",
            ),
        ),
        "secret reads limited to necessity": (
            2,
            "Trust & Safety",
            (
                "Do not read credential files or secret stores unless the current "
                "task requires it",
            ),
        ),
        "secret values never echoed": (
            2,
            "Trust & Safety",
            ("never echo secret values",),
        ),
        "every adaptation write is audited": (
            2,
            "Self-Evolution Protocol",
            ("every `.agents/` write appends a changelog entry",),
        ),
    },
    "AGENTS.zh-CN.md": {
        "当前消息优先与最近指令范围": (
            2,
            "信任与安全",
            (
                "当前消息优先于所有 `AGENTS.md`",
                "离目标产物最近且非依赖/生成目录内的 `AGENTS.md` 生效",
            ),
        ),
        "安装网络获取代码需当场确认": (
            2,
            "信任与安全",
            ("安装或运行网络获取的代码", "必须用户当场明确确认"),
        ),
        "项目误分类三类触发面": (
            2,
            "失败模式",
            ("项目类型、入口或验证命令不确定或受到质疑",),
        ),
        "无人值守默认拒绝": (
            2,
            "失败模式",
            ("把所有需确认的动作一律视为被拒绝",),
        ),
        "能力促升阈值": (
            3,
            "进化模型",
            ("至少 3 个不同任务", "最近 5 次记录"),
        ),
        "能力降级阈值": (
            3,
            "进化模型",
            ("最近 5 次至少 2 次", "90 天无使用记录"),
        ),
        "适配层必需目录": (
            3,
            "目录结构",
            (
                "project-overview.md",
                "source-index.md",
                "review-findings.md",
                "open-items.md",
                "outcomes.md",
                "secret-requirements.md",
                "├── rules/",
                "├── workflows/",
                "├── reports/",
                "├── experiments/",
                "├── tmp/",
                "├── skills/",
                "├── archive/",
                "└── changelog.md",
            ),
        ),
        "删除持久能力需确认": (
            3,
            "进化规则",
            (
                "| 删除 `rules/`、`workflows/`、`reports/`、`experiments/` 或 "
                "`skills/` | 需确认 |",
            ),
        ),
        "候选促升需确认": (
            3,
            "进化规则",
            (
                "| 从 `experiments/` 把候选促升到 `rules/`、`workflows/` 或 "
                "`skills/` | 需确认 |",
            ),
        ),
        "模板仅用官方同语言来源": (
            3,
            "更新本模板",
            ("官方同语言模板", "只能从 AgentGo 官方仓库替换"),
        ),
        "模板获取失败不得凭记忆重建": (
            3,
            "更新本模板",
            ("失败/无网络则停止；不得凭记忆重建或部分更新。",),
        ),
        "模板优先 release tag": (
            3,
            "更新本模板",
            ("优先最新 release tag 而非 `main`",),
        ),
        "模板敏感章节变化需确认": (
            3,
            "更新本模板",
            ("信任与安全、进化规则或硬性约束有变化仍需用户明确确认",),
        ),
        "维护规模与频率阈值": (
            3,
            "维护节奏",
            (
                "任一 `memory/` 文件超过 200 行",
                "`memory/` 总计约超过 3,000 行",
                "changelog 新增至少 30 行",
            ),
        ),
        "维护保护 pinned 与会话草稿": (
            3,
            "维护节奏",
            (
                "未协调的 `tmp/sessions/<session-id>/` 必须先合并或归档",
                "不清理/合并/归档 `status=pinned` 或旧 `<!-- pinned -->` 条目",
            ),
        ),
        "常规 changelog 格式": (
            3,
            "Changelog 格式",
            (
                "常规：`YYYY-MM-DD | <create|update|delete|merge|rename> | "
                "<path or artifact> | <what was done>`。",
            ),
        ),
        "扩展 changelog 格式与触发条件": (
            3,
            "Changelog 格式",
            (
                "删除、合并、`[MAINTENANCE]`、bootstrap 或重扫：",
                "`YYYY-MM-DDTHH:MM:SSZ | <agent>:<session> | <op|event> | "
                "<path or artifact> | <what> | <why>`",
            ),
        ),
        "仅在必要时读取 secret": (
            2,
            "信任与安全",
            ("除非当前任务需要，不读取凭据文件或 secret 存储",),
        ),
        "不回显 secret": (
            2,
            "信任与安全",
            ("绝不把 secret 真实值回显",),
        ),
        "每次适配写入都留审计记录": (
            2,
            "自我进化协议",
            ("每次 `.agents/` 写入都追加一条 changelog",),
        ),
    },
}

NORMATIVE_LINE_PATTERNS = {
    (
        "AGENTS.md",
        "network-fetched code installation requires confirmation",
    ): re.compile(
        r"^- \*\*High-risk side effects\*\*—"
        r"(?=[^\r\n]*installing or running network-fetched code)"
        r"[^\r\n]*—require explicit in-context user confirmation\.$",
        re.MULTILINE,
    ),
    ("AGENTS.zh-CN.md", "安装网络获取代码需当场确认"): re.compile(
        r"^- \*\*高风险副作用\*\*——"
        r"(?=[^\r\n]*安装或运行网络获取的代码)"
        r"[^\r\n]*——必须用户当场明确确认。$",
        re.MULTILINE,
    ),
}

BLOCKQUOTE_PREFIX_RE = re.compile(r" {0,3}>[ \t]?")


def extract_version(text: str) -> str | None:
    first_line = text.splitlines()[0] if text.splitlines() else ""
    match = VERSION_RE.fullmatch(first_line)
    return match.group("version") if match else None


def split_blockquote_prefix(line: str) -> tuple[int, str]:
    """Return the CommonMark blockquote depth and content of one line."""
    depth = 0
    offset = 0
    while match := BLOCKQUOTE_PREFIX_RE.match(line, offset):
        depth += 1
        offset = match.end()
    return depth, line[offset:]


def leading_indent_columns(line: str) -> int:
    """Measure leading Markdown indentation with four-column tab stops."""
    columns = 0
    for character in line:
        if character == " ":
            columns += 1
        elif character == "\t":
            columns += 4 - columns % 4
        else:
            break
    return columns


def mask_fenced_code_blocks(text: str) -> str:
    """Mask fenced and indented code while preserving character positions."""
    masked: list[str] = []
    fence_char: str | None = None
    fence_length = 0
    fence_blockquote_depth = 0

    for line in text.splitlines(keepends=True):
        blockquote_depth, content = split_blockquote_prefix(line)

        if (
            fence_char is not None
            and blockquote_depth < fence_blockquote_depth
        ):
            fence_char = None
            fence_length = 0
            fence_blockquote_depth = 0

        if fence_char is not None:
            closing = re.fullmatch(
                rf" {{0,3}}{re.escape(fence_char)}{{{fence_length},}}"
                r"[ \t]*(?:\r?\n)?",
                content,
            )
            if closing is not None and blockquote_depth == fence_blockquote_depth:
                fence_char = None
                fence_length = 0
                fence_blockquote_depth = 0
            masked.append(re.sub(r"[^\r\n]", " ", line))
            continue

        if leading_indent_columns(content) >= 4:
            masked.append(re.sub(r"[^\r\n]", " ", line))
            continue

        opening = re.match(r"^ {0,3}(?P<fence>`{3,}|~{3,})", content)
        if opening is not None:
            fence = opening.group("fence")
            fence_char = fence[0]
            fence_length = len(fence)
            fence_blockquote_depth = blockquote_depth
            masked.append(re.sub(r"[^\r\n]", " ", line))
            continue

        masked.append(line)

    return "".join(masked)


def extract_h2(text: str) -> list[str]:
    return re.findall(
        r"^## (.+)$", mask_fenced_code_blocks(text), flags=re.MULTILINE
    )


def extract_h3(text: str) -> list[str]:
    return re.findall(
        r"^### (.+)$", mask_fenced_code_blocks(text), flags=re.MULTILINE
    )


def extract_heading_section(text: str, level: int, heading: str) -> str:
    prefix = "#" * level
    masked = mask_fenced_code_blocks(text)
    match = re.search(
        rf"^{prefix} {re.escape(heading)}\n(?P<body>.*?)(?=^#{{1,{level}}} |\Z)",
        masked,
        flags=re.MULTILINE | re.DOTALL,
    )
    if match is None:
        return ""
    return text[match.start("body") : match.end("body")]


def extract_section(text: str, heading: str) -> str:
    return extract_heading_section(text, 2, heading)


def extract_failure_mode_ids(text: str, heading: str) -> list[str]:
    section = mask_fenced_code_blocks(extract_section(text, heading))
    return re.findall(
        r"^- \*\*([A-Z][A-Z0-9_]*)\*\*[：:]", section, re.MULTILINE
    )


def validate_semantics(english: str, chinese: str) -> list[str]:
    errors: list[str] = []
    for name, text in (("AGENTS.md", english), ("AGENTS.zh-CN.md", chinese)):
        for contract, (level, heading, markers) in SEMANTIC_MARKERS[name].items():
            section = extract_heading_section(text, level, heading)
            searchable = (
                section
                if (name, contract) in FENCED_MARKER_CONTRACTS
                else mask_fenced_code_blocks(section)
            )
            normative_line = NORMATIVE_LINE_PATTERNS.get((name, contract))
            if (
                not section
                or not all(marker in searchable for marker in markers)
                or (
                    normative_line is not None
                    and normative_line.search(searchable) is None
                )
            ):
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

    expected_english_h3 = [pair[0] for pair in H3_PAIRS]
    expected_chinese_h3 = [pair[1] for pair in H3_PAIRS]
    if extract_h3(english) != expected_english_h3:
        errors.append("AGENTS.md H3 names or order differ from the public contract")
    if extract_h3(chinese) != expected_chinese_h3:
        errors.append("AGENTS.zh-CN.md H3 names or order differ from the public contract")

    for english_h2, chinese_h2 in H2_PAIRS:
        expected_pairs = H3_PAIRS_BY_H2.get((english_h2, chinese_h2), ())
        expected_english_h3 = [pair[0] for pair in expected_pairs]
        expected_chinese_h3 = [pair[1] for pair in expected_pairs]
        english_h3 = extract_h3(extract_section(english, english_h2))
        chinese_h3 = extract_h3(extract_section(chinese, chinese_h2))
        if english_h3 != expected_english_h3:
            errors.append(
                f"AGENTS.md H3 names or order under {english_h2} differ from "
                "the public contract"
            )
        if chinese_h3 != expected_chinese_h3:
            errors.append(
                f"AGENTS.zh-CN.md H3 names or order under {chinese_h2} differ "
                "from the public contract"
            )

    english_ids = extract_failure_mode_ids(english, H2_PAIRS[3][0])
    chinese_ids = extract_failure_mode_ids(chinese, H2_PAIRS[3][1])
    if english_ids != chinese_ids:
        errors.append(
            "failure-mode IDs differ: "
            f"AGENTS.md={english_ids}, AGENTS.zh-CN.md={chinese_ids}"
        )
    expected_failure_mode_ids = list(FAILURE_MODE_IDS)
    for name, ids in (("AGENTS.md", english_ids), ("AGENTS.zh-CN.md", chinese_ids)):
        if ids != expected_failure_mode_ids:
            errors.append(
                f"{name} failure-mode IDs differ from the fixed contract: "
                f"expected={expected_failure_mode_ids}, actual={ids}"
            )

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
