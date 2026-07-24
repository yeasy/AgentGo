# Contributing to AgentGo

Thanks for helping! The bar for changes: **stay lean and generic** — if a change doesn't help at least three different AI tools, it probably doesn't belong here. Open an issue first for structural changes. Small doc/tooling fixes can go straight to PR; any edit to `AGENTS.md` / `AGENTS.zh-CN.md` also needs the release-lock step below, so it is never a one-line change.

## Bilingual sync (enforced by CI)

English and Simplified Chinese files are maintained in parallel:

- `AGENTS.md` and `AGENTS.zh-CN.md` must keep matching **version markers**, mapped public **section structure**, failure-mode IDs, and critical protocol contracts.
- `README.md` and `README.zh-CN.md` must keep corresponding headings and stable-version examples synchronized.

Every PR that changes meaning in one language must update the other. Contract tests validate semantic structure without requiring identical physical line counts or heading line numbers; CI (`.github/workflows/docs.yml`) fails on covered drift.

## Running the contract suite

Run the complete contract suite before submitting changes:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

## Editing AGENTS.md (release locks)

The validator pins each protocol file by SHA-256 (a whole-file content lock plus per-line and directory-tree digests in `scripts/validate_docs.py`). **Any** edit to `AGENTS.md` or `AGENTS.zh-CN.md` therefore fails the suite with `content differs from the release lock` until the digests are regenerated. Do not hand-edit the hashes — regenerate them:

```bash
python3 scripts/regen_locks.py           # check whether locks are stale
python3 scripts/regen_locks.py --write    # rewrite the digests + RELEASE_LOCK_VERSION
```

Bump the version marker on line 1 of both files first (see below), then run `--write`, then re-run the contract suite. Keep `AGENTS.md` and `AGENTS.zh-CN.md` on the same version, and update the `v<version>` examples in both READMEs to match.

The whole-file content lock is the real tamper-evidence; the per-line semantic contracts are drift *diagnostics* that name which rule changed, not a guarantee against a determined editor who also regenerates the digests — always review the prose diff. Keep that layer small rather than adding a contract per rule.

## Versioning and releases

- The first line of `AGENTS.md` carries the template version: `<!-- AGENTS.md vX.Y.Z ... -->`.
- SemVer-like rules (see "Updating This Template" in `AGENTS.md`): **patch** = wording/clarity fixes, **minor** = backward-compatible protocol behavior, **major** = incompatible source-priority, permission, or layout changes.
- Only changes to `AGENTS.md` bump the version and get a release tag; README/docs-only changes ride on `main` untagged.
- Every release tag gets release notes describing the protocol changes — downstream agents are told to cite release notes when suggesting template updates, so they must exist.

## Commit style

`type(scope): description`, for example `docs(protocol): v1.8.0 — tighten extraction provenance`.
