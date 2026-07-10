# Contributing to AgentGo

Thanks for helping! The bar for changes: **stay lean and generic** — if a change doesn't help at least three different AI tools, it probably doesn't belong here. Open an issue first for structural changes; bug fixes and small template improvements can go straight to PR.

## Bilingual sync (enforced by CI)

English and Simplified Chinese files are maintained in parallel:

- `AGENTS.md` and `AGENTS.zh-CN.md` must keep matching **version markers**, mapped public **section structure**, failure-mode IDs, and critical protocol contracts.
- `README.md` and `README.zh-CN.md` must keep corresponding headings and stable-version examples synchronized.

Every PR that changes meaning in one language must update the other. Contract tests validate semantic structure without requiring identical physical line counts or heading line numbers; CI (`.github/workflows/docs.yml`) fails on covered drift.

## Conformance corpus

`evals/scenarios.json` is a protocol conformance corpus, not cross-tool pass evidence. Keep runs isolated, disable network access, stub external side effects, use synthetic secrets only, and update `protocol_version` whenever the template version changes.

Run the complete contract suite before submitting changes:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

## Versioning and releases

- The first line of `AGENTS.md` carries the template version: `<!-- AGENTS.md vX.Y.Z ... -->`.
- SemVer-like rules (see "Updating This Template" in `AGENTS.md`): **patch** = wording/clarity fixes, **minor** = backward-compatible protocol behavior, **major** = incompatible source-priority, permission, or layout changes.
- Only changes to `AGENTS.md` bump the version and get a release tag; README/docs-only changes ride on `main` untagged.
- Every release tag gets release notes describing the protocol changes — downstream agents are told to cite release notes when suggesting template updates, so they must exist.

## Commit style

`type(scope): description`, for example `docs(protocol): v1.8.0 — tighten extraction provenance`.
