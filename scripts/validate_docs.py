#!/usr/bin/env python3
"""Validate the bilingual AgentGo protocol contract using only the stdlib."""

from __future__ import annotations

import re
import stat
import sys
from hashlib import sha256
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 28_672
RELEASE_LOCK_VERSION = "1.13.1"
PROTOCOL_CONTENT_DIGESTS = {
    "AGENTS.md": "13dc0317669fcef7baadac808181d3d8cdd22c08322c041e3fb91613e55af911",
    "AGENTS.zh-CN.md": "a511ba19835dfe155a48f32e66d84e421e6ced3b39873a086d09a3bcbfbeac0d",
}
NUMERIC_IDENTIFIER = r"(?:0|[1-9][0-9]*)"
NON_NUMERIC_IDENTIFIER = r"(?:[0-9]*[A-Za-z-][0-9A-Za-z-]*)"
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

# Exact canonical-line hashes keep safety contracts compact and non-substring-based.
AUTHORITATIVE_LINE_DIGESTS = {
    "AGENTS.md": {
        "authority": "13a54883bcba942b4898fa2d7a44acf75a3fae34ff2bc13fe93772757c16166c",
        "high_risk": "5e29a4a4c71ff1f5ea58e596d03b4af87128d476fd7dc47577441afed87ecf6e",
        "misclassified": "dd98199f4a2057875bb46e0027d548e9b8587254cef51fd1ddba751c2b43c1a6",
        "unattended": "3c193024bb9186c0c24db13479f5abf851f46465b08bb8f2ef89027717074191",
        "secret": "8b3865402a87534747fd3db84aac145a1d2392b989258adbb34ee4cbdedb1a43",
        "promotion_threshold": "d52f86d562828594b67f2e1c29d61da82f47fd68b7197ef0c64bca0341446f3e",
        "demotion_threshold": "2006d3fd5c034c068048485bc09e4b5dfbff722b97029434613e31e66257aa0b",
        "deletion_row": "f8b823fe1cbe69f2342b6e170fd20751476572ca09a8fbf331ed63cd0570de8b",
        "promotion_row": "ee401f7dcd7c34620a414595f53e44a81aae137f3b4f71f9303f663688a532dc",
        "template_download": "84e319f4f38a8846d9336efdfb1aa708cf2aa6bba9d87986ef533bb136adcaf1",
        "template_replace": "92152ec46e036da4e8826959ea806c426416382ff352566f715c72c343b55272",
        "maintenance_temp": "0ea7edc01e20b175811031d5a5b58fcfe552d58204593267b13f2cb54d286f69",
        "maintenance_pinned": "69256654d6d626cccdd35d07b23916e94543698a291e8e61dffe7c4bbd85911f",
        "audit": "e98935f58abe0c9bf66946642c2b98e46e26c02a1769728002b4832c36a7357b",
    },
    "AGENTS.zh-CN.md": {
        "authority": "711be38d5998cb4b3b7d4a8eab4c30c645c5d76f204ab5091a8c31da9cb7730c",
        "high_risk": "f62a6ee94d1f973ec587fec064e70e6b1089ca95da639715120f679268c9e35d",
        "misclassified": "3d56c9568f0fd3d028f083cedac65c1c259ad9811f7ee0b2dedd5ccbffc0e418",
        "unattended": "12ac32897b07a45e493caf6ca314f4946035a1f977efd8473d19ca1b35d8575d",
        "secret": "85271e40756bc7e278a25352eb5bd8d2b4d7792e8c2143f8c4f75f9849bde603",
        "promotion_threshold": "34c9bf99f5f2b4748e3e0b9c4d9c6179f09021ddead82b60abfbaa590d7d947b",
        "demotion_threshold": "da475ab88dc5830c6c9e13fb8dc0df47dfba6db5a2d19d88bf521193da5cc4f5",
        "deletion_row": "84135f311d4110b6ee133393d47e972b7fecc88a6300446434f5231921d1f5d6",
        "promotion_row": "f59eda32e0430bfffab1f2692675648d9c65cac25d58df3a6af0a5d4a26a7d65",
        "template_download": "d6cc5e76e5832a5a2c1a952b1c2624a8aa77eb053f0a0d82035ab79853bc6bec",
        "template_replace": "b5b59f3e5fa23ecb1e472ea01565bce65f4b575c607e982109856c57c1930e08",
        "maintenance_temp": "34a39799219d5431322b1141584e33b7d2e0c1464d3eb2365cdc405aaba36c25",
        "maintenance_pinned": "ff9c19c6167772c8012701dd9908b6c584ee482c3fe9e2975d70eb622ecadc22",
        "audit": "627b799167524888729de02b9309f67df7e2ee3df1530272ca79443f4bff2470",
    },
}

AUTHORITATIVE_CONTRACT_LINE_KEYS = {
    "AGENTS.md": {
        "current-message priority and closest instruction scope": ("authority",),
        "network-fetched code installation requires confirmation": ("high_risk",),
        "misclassified-project trigger surfaces": ("misclassified",),
        "unattended default decline": ("unattended",),
        "capability promotion thresholds": ("promotion_threshold",),
        "capability demotion thresholds": ("demotion_threshold",),
        "persistent capability deletion confirmation": ("deletion_row",),
        "candidate promotion confirmation": ("promotion_row",),
        "template official same-language source": (
            "template_download",
            "template_replace",
        ),
        "template fetch failure stops without reconstruction": ("template_download",),
        "template release tag preference": ("template_replace",),
        "template sensitive-section confirmation": ("template_replace",),
        "maintenance pinned and session protection": (
            "maintenance_temp",
            "maintenance_pinned",
        ),
        "secret reads limited to necessity": ("secret",),
        "secret values never echoed": ("secret",),
        "every adaptation write is audited": ("audit",),
    },
    "AGENTS.zh-CN.md": {
        "当前消息优先与最近指令范围": ("authority",),
        "安装网络获取代码需当场确认": ("high_risk",),
        "项目误分类三类触发面": ("misclassified",),
        "无人值守默认拒绝": ("unattended",),
        "能力促升阈值": ("promotion_threshold",),
        "能力降级阈值": ("demotion_threshold",),
        "删除持久能力需确认": ("deletion_row",),
        "候选促升需确认": ("promotion_row",),
        "模板仅用官方同语言来源": ("template_download", "template_replace"),
        "模板获取失败不得凭记忆重建": ("template_download",),
        "模板优先 release tag": ("template_replace",),
        "模板敏感章节变化需确认": ("template_replace",),
        "维护保护 pinned 与会话草稿": (
            "maintenance_temp",
            "maintenance_pinned",
        ),
        "仅在必要时读取 secret": ("secret",),
        "不回显 secret": ("secret",),
        "每次适配写入都留审计记录": ("audit",),
    },
}

DIRECTORY_TREE_DIGESTS = {
    "AGENTS.md": "525a8024e1688adcf015ac82212c6df05bace83a4ed247f88d024d6bd2a788e3",
    "AGENTS.zh-CN.md": "1d8596b32b31aa7f4fb7684cae3b04a583007c8238826b4b627f65c83880274d",
}
DIRECTORY_TREE_RE = re.compile(r"^```[ \t]*\n.*?^```[ \t]*$", re.MULTILINE | re.DOTALL)

BLOCKQUOTE_PREFIX_RE = re.compile(r" {0,3}>[ \t]?")
LIST_MARKER_RE = re.compile(
    r" {0,3}(?P<marker>[-+*]|[0-9]{1,9}[.)])(?P<padding>[ \t]{1,4})"
)
FENCE_OPEN_RE = re.compile(
    r"^ {0,3}(?P<fence>`{3,}|~{3,})(?P<info>[^\r\n]*)(?:\r?\n)?$"
)
RAW_HTML_OPEN_RE = re.compile(
    r"<(?P<tag>pre|script|style|textarea)(?=[\s>])",
    re.IGNORECASE,
)


def extract_version(text: str) -> str | None:
    first_line = text.splitlines()[0] if text.splitlines() else ""
    match = VERSION_RE.fullmatch(first_line)
    return match.group("version") if match else None


def content_digest(text: str) -> str:
    """Return the release-lock digest for a protocol document."""
    return sha256(text.encode("utf-8")).hexdigest()


def read_protocol_file(path: Path) -> str:
    """Read one UTF-8 protocol artifact without following non-regular files."""
    try:
        mode = path.lstat().st_mode
    except OSError as error:
        raise ValueError(f"{path.name} must be a regular file") from error
    if not stat.S_ISREG(mode):
        raise ValueError(f"{path.name} must be a regular file")
    try:
        return path.read_bytes().decode("utf-8")
    except (OSError, UnicodeError) as error:
        raise ValueError(f"{path.name} must be readable UTF-8") from error


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


def display_columns(text: str) -> int:
    """Measure text columns using Markdown's four-column tab stops."""
    columns = 0
    for character in text:
        if character == "\t":
            columns += 4 - columns % 4
        else:
            columns += 1
    return columns


def mask_range(characters: list[str], start: int, end: int) -> None:
    for index in range(start, end):
        if characters[index] not in "\r\n":
            characters[index] = " "


def find_code_span_end(text: str, start: int, run_length: int) -> int | None:
    delimiter = "`" * run_length
    closing = re.compile(
        rf"(?<!`){re.escape(delimiter)}(?!`)",
    ).search(text, start + run_length)
    return closing.end() if closing is not None else None


def mask_html_non_prose(text: str) -> str:
    """Mask HTML comments/raw blocks without masking inline-code examples."""
    characters = list(text)
    index = 0
    while index < len(text):
        if text[index] == "`":
            run_end = index + 1
            while run_end < len(text) and text[run_end] == "`":
                run_end += 1
            code_end = find_code_span_end(text, index, run_end - index)
            index = code_end if code_end is not None else run_end
            continue

        if text.startswith("<!--", index):
            closing = text.find("-->", index + 4)
            end = len(text) if closing < 0 else closing + 3
            mask_range(characters, index, end)
            index = end
            continue

        raw_opening = RAW_HTML_OPEN_RE.match(text, index)
        if raw_opening is not None:
            tag = raw_opening.group("tag")
            closing = re.compile(
                rf"</{re.escape(tag)}\s*>",
                re.IGNORECASE,
            ).search(text, raw_opening.end())
            end = len(text) if closing is None else closing.end()
            mask_range(characters, index, end)
            index = end
            continue

        index += 1

    return "".join(characters)


def parse_container_prefix(line: str) -> tuple[tuple[tuple[str, int], ...], str]:
    """Strip leading blockquote/list markers and describe their continuation."""
    operations: list[tuple[str, int]] = []
    offset = 0
    while True:
        blockquote = BLOCKQUOTE_PREFIX_RE.match(line, offset)
        if blockquote is not None:
            operations.append(("quote", 0))
            offset = blockquote.end()
            continue

        list_marker = LIST_MARKER_RE.match(line, offset)
        if list_marker is not None:
            prefix = line[offset : list_marker.end()]
            operations.append(("list", display_columns(prefix)))
            offset = list_marker.end()
            continue

        break

    return tuple(operations), line[offset:]


def consume_indentation(line: str, offset: int, required: int) -> int | None:
    columns = 0
    index = offset
    while index < len(line) and line[index] in " \t" and columns < required:
        if line[index] == "\t":
            columns += 4 - columns % 4
        else:
            columns += 1
        index += 1
    return index if columns >= required else None


def consume_container_continuation(
    line: str,
    operations: tuple[tuple[str, int], ...],
) -> str | None:
    offset = 0
    for kind, width in operations:
        if kind == "quote":
            blockquote = BLOCKQUOTE_PREFIX_RE.match(line, offset)
            if blockquote is None:
                return None
            offset = blockquote.end()
        else:
            continuation = consume_indentation(line, offset, width)
            if continuation is None:
                return None
            offset = continuation
    return line[offset:]


def fence_opening(content: str) -> tuple[str, int] | None:
    opening = FENCE_OPEN_RE.fullmatch(content)
    if opening is None:
        return None
    fence = opening.group("fence")
    if fence[0] == "`" and "`" in opening.group("info"):
        return None
    return fence[0], len(fence)


def is_fence_closing(content: str, character: str, length: int) -> bool:
    return (
        re.fullmatch(
            rf" {{0,3}}{re.escape(character)}{{{length},}}"
            r"[ \t]*(?:\r?\n)?",
            content,
        )
        is not None
    )


def is_blank_line(line: str) -> bool:
    return not line.strip(" \t\r\n")


def starts_nonparagraph_block(content: str) -> bool:
    stripped = content.lstrip(" \t")
    return re.match(r"#{1,6}(?:[ \t]+|$)", stripped) is not None


def mask_fenced_code_blocks(text: str) -> str:
    """Mask non-prose Markdown/HTML regions while preserving character positions."""
    text = mask_html_non_prose(text)
    masked: list[str] = []
    fence_char: str | None = None
    fence_length = 0
    fence_containers: tuple[tuple[str, int], ...] = ()
    indented_code_open = False
    paragraph_open = False

    for line in text.splitlines(keepends=True):
        while True:
            if fence_char is not None:
                if is_blank_line(line):
                    masked.append(re.sub(r"[^\r\n]", " ", line))
                    break
                content = consume_container_continuation(line, fence_containers)
                if content is None:
                    fence_char = None
                    fence_length = 0
                    fence_containers = ()
                    paragraph_open = False
                    continue
                if is_fence_closing(content, fence_char, fence_length):
                    fence_char = None
                    fence_length = 0
                    fence_containers = ()
                masked.append(re.sub(r"[^\r\n]", " ", line))
                break

            if indented_code_open:
                if is_blank_line(line):
                    masked.append(re.sub(r"[^\r\n]", " ", line))
                    break
                _, content = parse_container_prefix(line)
                if leading_indent_columns(content) >= 4:
                    masked.append(re.sub(r"[^\r\n]", " ", line))
                    break
                indented_code_open = False
                continue

            if is_blank_line(line):
                masked.append(line)
                paragraph_open = False
                break

            containers, content = parse_container_prefix(line)
            opening = fence_opening(content)
            if opening is not None:
                fence_char, fence_length = opening
                fence_containers = containers
                paragraph_open = False
                masked.append(re.sub(r"[^\r\n]", " ", line))
                break

            if leading_indent_columns(content) >= 4 and not paragraph_open:
                indented_code_open = True
                masked.append(re.sub(r"[^\r\n]", " ", line))
                break

            masked.append(line)
            paragraph_open = not starts_nonparagraph_block(content)
            break

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
            directory_contract = contract in {
                "required adaptation directories",
                "适配层必需目录",
            }
            if directory_contract:
                visible_section = mask_html_non_prose(section)
                block_digests = [
                    sha256(match.group(0).encode()).hexdigest()
                    for match in DIRECTORY_TREE_RE.finditer(visible_section)
                ]
                valid = block_digests.count(DIRECTORY_TREE_DIGESTS[name]) == 1
            else:
                searchable = mask_fenced_code_blocks(section)
                line_digests = [
                    sha256(line.encode()).hexdigest()
                    for line in searchable.splitlines()
                ]
                line_keys = AUTHORITATIVE_CONTRACT_LINE_KEYS[name].get(contract, ())
                authoritative = all(
                    line_digests.count(AUTHORITATIVE_LINE_DIGESTS[name][key]) == 1
                    for key in line_keys
                )
                valid = all(marker in searchable for marker in markers) and authoritative
            if not section or not valid:
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
    oversized = False

    for name, text in documents:
        size = len(text.encode("utf-8"))
        if size > max_bytes:
            oversized = True
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

    if oversized:
        return errors

    for name, text in documents:
        if content_digest(text) != PROTOCOL_CONTENT_DIGESTS[name]:
            errors.append(
                f"{name} content differs from the v{RELEASE_LOCK_VERSION} "
                "release lock"
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
    try:
        english = read_protocol_file(english_path)
        chinese = read_protocol_file(chinese_path)
    except ValueError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
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
