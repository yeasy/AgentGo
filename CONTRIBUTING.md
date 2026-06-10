# Contributing to AgentGo

Thanks for helping! The bar for changes: **stay lean and generic** — if a change doesn't help at least three different AI tools, it probably doesn't belong here. Open an issue first for structural changes; bug fixes and small template improvements can go straight to PR.

## Bilingual sync (enforced by CI)

English and Simplified Chinese files are maintained in parallel:

- `AGENTS.md` and `AGENTS.zh-CN.md` must have the **same line count** and the **same version marker** in line 1.
- `README.md` and `README.zh-CN.md` must have their **headings on the same line numbers**.

Every PR that touches one language must apply the same-shaped edit to the other. CI (`.github/workflows/docs.yml`) fails on drift.

## Versioning and releases

- The first line of `AGENTS.md` carries the template version: `<!-- AGENTS.md vX.Y.Z ... -->`.
- SemVer-like rules (see "Updating This Template" in `AGENTS.md`): **patch** = wording/clarity fixes, **minor** = backward-compatible protocol behavior, **major** = incompatible source-priority, permission, or layout changes.
- Only changes to `AGENTS.md` bump the version and get a release tag; README/docs-only changes ride on `main` untagged.
- Every release tag gets release notes describing the protocol changes — downstream agents are told to cite release notes when suggesting template updates, so they must exist.

## Commit style

`type(scope): description`, for example `docs(protocol): v1.8.0 — tighten extraction provenance`.
