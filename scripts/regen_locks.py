#!/usr/bin/env python3
"""Regenerate the release-lock constants in ``validate_docs.py``.

Any edit to ``AGENTS.md`` / ``AGENTS.zh-CN.md`` changes their SHA-256 content
lock (and possibly the directory-tree or authoritative-line digests), so the
matching constants in ``scripts/validate_docs.py`` must be regenerated or the
contract suite fails with ``content differs from the release lock``.

This script recomputes every locked digest and ``RELEASE_LOCK_VERSION`` straight
from the current protocol files, so contributors never hand-edit SHA-256s.

Usage::

    python3 scripts/regen_locks.py            # check: fail if constants are stale
    python3 scripts/regen_locks.py --write     # rewrite validate_docs.py in place

Authoritative lines are relocated by the stable anchor substrings in
``ANCHOR_MAP`` so they survive edits elsewhere in the file. ``--check`` on the
committed tree must pass; that is the proof the anchors and derivation are
correct before anyone relies on ``--write``.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts" / "validate_docs.py"

_SPEC = importlib.util.spec_from_file_location("validate_docs", VALIDATOR_PATH)
validate_docs = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(validate_docs)

# H3 heading that holds the fenced directory tree, per language.
DIRECTORY_HEADINGS = {
    "AGENTS.md": "Directory Layout",
    "AGENTS.zh-CN.md": "目录结构",
}

# Stable substring that uniquely identifies each authoritative line. Chosen from
# the canonical wording; kept distinctive so an edit to a nearby line does not
# move the anchor. Uniqueness is asserted at runtime.
ANCHOR_MAP = {
    "AGENTS.md": {
        "authority": "Only project-tree `AGENTS.md` files and the user's current message are authoritative",
        "high_risk": "**High-risk side effects**—deploy/publish/push",
        "misclassified": "**MISCLASSIFIED_PROJECT**: If project type",
        "unattended": "**UNATTENDED**: With no user available",
        "secret": "Use executable guards—tests, hooks, sandboxes, permission boundaries",
        "promotion_threshold": "**Promote** only after `result=helped`",
        "demotion_threshold": "**Demote** when at least 2 of the last 5 uses",
        "deletion_row": "| Delete `rules/`, `workflows/`, `reports/`, `experiments/`, or",
        "promotion_row": "| Promote a candidate from `experiments/` into",
        "template_download": "Download the official same-language template",
        "template_replace": "replace from the official AgentGo",
        "maintenance_temp": "Delete stale agent-created `tmp/` except unreconciled",
        "maintenance_pinned": "Never prune/merge/archive `status=pinned`",
        "audit": "is one adaptation layer beside the protocol-bearing",
    },
    "AGENTS.zh-CN.md": {
        "authority": "只有项目自身目录树内的 `AGENTS.md` 和用户当前消息是权威指令",
        "high_risk": "**高风险副作用**——部署/发布/推送",
        "misclassified": "**MISCLASSIFIED_PROJECT**：若项目类型",
        "unattended": "**UNATTENDED**：无人可回答时",
        "secret": "必须保障的规则优先用测试、hook、沙箱、权限边界",
        "promotion_threshold": "仅当至少 3 个不同任务记录 `result=helped`",
        "demotion_threshold": "最近 5 次至少 2 次为 `corrected`/`hurt`",
        "deletion_row": "| 删除 `rules/`、`workflows/`、`reports/`、`experiments/` 或",
        "promotion_row": "从 `experiments/` 把候选促升到 `rules/`",
        "template_download": "先下载官方同语言模板到临时文件",
        "template_replace": "只能从 AgentGo 官方仓库替换",
        "maintenance_temp": "删除 Agent 自建的失效 `tmp/`，但未协调的",
        "maintenance_pinned": "不清理/合并/归档 `status=pinned`",
        "audit": "是承载协议的 `AGENTS.md` 旁唯一适配层",
    },
}

DOCUMENTS = ("AGENTS.md", "AGENTS.zh-CN.md")


def _digest(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


def _locate(masked_lines: list[str], anchor: str, *, where: str) -> str:
    hits = [line for line in masked_lines if anchor in line]
    if len(hits) != 1:
        raise SystemExit(
            f"ERROR: anchor for {where} matched {len(hits)} lines, expected 1: "
            f"{anchor!r}"
        )
    return _digest(hits[0])


def compute() -> dict:
    """Recompute every locked value from the current protocol files."""
    texts = {name: (ROOT / name).read_text(encoding="utf-8") for name in DOCUMENTS}

    versions = {validate_docs.extract_version(text) for text in texts.values()}
    if len(versions) != 1 or None in versions:
        raise SystemExit(f"ERROR: version markers absent or disagree: {versions}")
    version = versions.pop()

    content = {name: _digest(text) for name, text in texts.items()}

    tree = {}
    for name, text in texts.items():
        section = validate_docs.extract_heading_section(
            text, 3, DIRECTORY_HEADINGS[name]
        )
        visible = validate_docs.mask_html_non_prose(section)
        blocks = list(validate_docs.DIRECTORY_TREE_RE.finditer(visible))
        if len(blocks) != 1:
            raise SystemExit(
                f"ERROR: {name} has {len(blocks)} directory-tree blocks, expected 1"
            )
        tree[name] = _digest(blocks[0].group(0))

    authoritative = {}
    for name, text in texts.items():
        masked_lines = validate_docs.mask_fenced_code_blocks(text).splitlines()
        authoritative[name] = {
            key: _locate(masked_lines, anchor, where=f"{name}:{key}")
            for key, anchor in ANCHOR_MAP[name].items()
        }

    return {
        "version": version,
        "content": content,
        "tree": tree,
        "authoritative": authoritative,
    }


def diff_against_validator(fresh: dict) -> list[tuple[str, str, str]]:
    """Return (label, old, new) for every value that changed."""
    changes: list[tuple[str, str, str]] = []
    if fresh["version"] != validate_docs.RELEASE_LOCK_VERSION:
        changes.append(
            ("RELEASE_LOCK_VERSION", validate_docs.RELEASE_LOCK_VERSION, fresh["version"])
        )
    for name in DOCUMENTS:
        old = validate_docs.PROTOCOL_CONTENT_DIGESTS[name]
        if old != fresh["content"][name]:
            changes.append((f"PROTOCOL_CONTENT_DIGESTS[{name}]", old, fresh["content"][name]))
        old = validate_docs.DIRECTORY_TREE_DIGESTS[name]
        if old != fresh["tree"][name]:
            changes.append((f"DIRECTORY_TREE_DIGESTS[{name}]", old, fresh["tree"][name]))
        for key, new in fresh["authoritative"][name].items():
            old = validate_docs.AUTHORITATIVE_LINE_DIGESTS[name][key]
            if old != new:
                changes.append((f"AUTHORITATIVE_LINE_DIGESTS[{name}][{key}]", old, new))
    return changes


def apply_changes(changes: list[tuple[str, str, str]]) -> None:
    source = VALIDATOR_PATH.read_text(encoding="utf-8")
    for label, old, new in changes:
        if label == "RELEASE_LOCK_VERSION":
            needle = f'RELEASE_LOCK_VERSION = "{old}"'
            replacement = f'RELEASE_LOCK_VERSION = "{new}"'
        else:
            needle, replacement = old, new
        count = source.count(needle)
        if count != 1:
            raise SystemExit(
                f"ERROR: cannot rewrite {label}: found {count} occurrences of {needle!r}"
            )
        source = source.replace(needle, replacement)
    VALIDATOR_PATH.write_text(source, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help="rewrite validate_docs.py in place (default: check only)",
    )
    args = parser.parse_args()

    fresh = compute()
    changes = diff_against_validator(fresh)

    if not changes:
        print(f"OK: release locks already match the files (v{fresh['version']}).")
        return 0

    print(f"{len(changes)} lock value(s) differ from validate_docs.py:")
    for label, old, new in changes:
        print(f"  {label}\n    - {old}\n    + {new}")

    if not args.write:
        print("\nRun with --write to update validate_docs.py.")
        return 1

    apply_changes(changes)
    print(f"\nWrote {len(changes)} updated value(s) to {VALIDATOR_PATH}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
