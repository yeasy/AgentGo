<h1 align="center">agentrc</h1>

<p align="center">
  <strong>The drop-in guide for AI agents.</strong>
</p>

<p align="center">
  <sub>Best practices baked in — works in every project.</sub>
</p>

<p align="center">English | <a href="./README.zh-CN.md">简体中文</a></p>

<p align="center">
  <a href="#getting-started">Getting Started</a> •
  <a href="#compatibility">Compatibility</a> •
  <a href="#how-it-works">How It Works</a> •
  <a href="#faq">FAQ</a>
</p>

<p align="center">
  <a href="https://agents.md/"><img src="https://img.shields.io/badge/AGENTS.md-spec_compliant-brightgreen" alt="AGENTS.md spec"></a>
  <img src="https://img.shields.io/badge/Claude_Code-compatible-blueviolet?logo=anthropic" alt="Claude Code">
  <img src="https://img.shields.io/badge/Codex-compatible-blue?logo=openai" alt="Codex">
  <img src="https://img.shields.io/badge/Cursor-compatible-orange" alt="Cursor">
  <img src="https://img.shields.io/badge/Copilot-compatible-lightgrey?logo=github" alt="Copilot">
  <img src="https://img.shields.io/badge/Windsurf-compatible-teal" alt="Windsurf">
  <img src="https://img.shields.io/badge/Gemini_CLI-compatible-yellow?logo=google" alt="Gemini CLI">
  <img src="https://img.shields.io/github/license/yeasy/agentrc" alt="License">
</p>

---

## What It Solves

Models are already capable enough. What actually blocks product quality is **how agent-engineering best practices land in your own project** — and **you shouldn't have to research and configure that yourself**:

- Harness design, context management, memory upkeep, safety guardrails… top-tier practices are scattered across blog posts
- Claude Code / Codex / Cursor / Copilot / Windsurf / Gemini each have their own config format, and the same rules get rewritten over and over
- Once you do write down project conventions, the knowledge stays trapped in chat history; the longer the session, the more noise it accumulates

**What agentrc gives you:** a best-practice [AGENTS.md spec](https://raw.githubusercontent.com/yeasy/agentrc/main/AGENTS.md) — drop it in your project root, and every mainstream agent immediately works to best practices and self-maintains project memory. **No configuration on your part.**

|                          | Without agentrc                                | With agentrc                                          |
|:-------------------------|:-----------------------------------------------|:------------------------------------------------------|
| **Cross-tool reuse**     | One ruleset per tool, rewrite when you switch IDE | One `AGENTS.md` travels with the code, works everywhere |
| **Best practices**       | Scattered, re-researched per project           | Out of the box: conventions, flow, safety, upkeep cadence |
| **Self-improvement**     | Needs constant human reminders                 | Auto-learns and evolves — gets smarter over time      |
| **Project knowledge**    | Stuck in chat history, dies when the session ends | Persisted in `.agents/`, agent maintains and prunes itself |
| **Old-config absorption**| `.cursorrules`, `CLAUDE.md`, etc. scattered everywhere | Detect → extract → archive to `.backup/` after you confirm |

---

## Getting Started

One step: download [AGENTS.md](https://github.com/yeasy/agentrc/blob/main/AGENTS.md) into your project root.

```bash
curl -fsSL https://raw.githubusercontent.com/yeasy/agentrc/main/AGENTS.md -o AGENTS.md
```

Then reopen Codex / Claude Code / Copilot / Cursor / Gemini / Windsurf — your agent suddenly gets smarter and starts managing the project to best practices.

> **Windows users:** on PowerShell 5, use `Invoke-WebRequest -Uri <URL> -OutFile AGENTS.md`.

## First Run

After downloading `AGENTS.md` and restarting your agent, try this prompt:

> **"Initialize this project per AGENTS.md. Execute step by step and report each step's result; if `.agents/` already exists, rescan and report diffs without overwriting."**

> The agent will ask for permission to write/move files — **please grant it**, otherwise it can only output suggestions without acting on them.

The agent will:
1. Scan your project structure and auto-fill the "Project Info" / "Project Commands & Conventions" blocks
2. Detect any existing `.cursorrules` / `CLAUDE.md` / `docs/` etc., list an archive plan and file diffs **for your confirmation**
3. Create `.agents/memory/project-overview.md`

From then on, every session begins with the agent reading `.agents/` before doing anything. Ask "why is this written this way?" — it can pull historical decisions from `decisions.md`. Carve out a new module — it follows the naming conventions in `rules/`.

---

## How It Works

### Boot Flow

Every time the AI agent opens your project, it runs this flow:

```mermaid
flowchart LR
    A["Read AGENTS.md"] --> B{".agents/ exists?"}
    B -->|Yes| C["Load memory/"]
    B -->|No| D["Scan project"]
    D --> E["Absorb existing config"]
    E --> F["Create .agents/"]
    C --> G["Start working"]
    F --> G
```

### Self-Evolution Loop

`.agents/` is continuously maintained by the agent — **only useful entries stay; stale ones get pruned**:

```mermaid
flowchart LR
    A["Read .agents/\nEnter with project context"] --> B["Execute task"]
    B --> C["New findings\n→ write to right category"]
    C --> D["Periodic review\nmerge / clean / drop stale"]
    D --> A

    style A fill:#2196F3,color:#fff
    style D fill:#FF9800,color:#fff
```

New findings are filed by type: coding conventions → `rules/`, architecture decisions → `memory/decisions.md`, gotchas → `memory/gotchas.md`, code patterns → `memory/patterns.md`, tech debt → `memory/tech-debt.md`. The maintenance cadence is enforced by `AGENTS.md` itself — **easy to write in, hard to stay** — so notes never pile up into noise.

### Brownfield Auto-Adoption

If your project already has `.cursorrules` / `CLAUDE.md` / `.windsurfrules` / `.github/copilot-instructions.md` etc. scattered around, the agent will, on its first session:

1. Scan all existing config files
2. Extract the knowledge into `.agents/`
3. List a discovery report and proposed archive plan
4. **Wait for your nod** before moving the old files into `.backup/`

Nothing is lost; every archive action requires your confirmation.

### Directory Layout

After a few sessions, your project ends up like this:

```
your-project/
├── AGENTS.md              ← The only file you add (human-controlled)
├── .agents/               ← Auto-created by the agent (grows with use)
│   ├── memory/            # Project overview, decisions, gotchas, patterns
│   ├── rules/             # Coding conventions extracted from the codebase
│   ├── workflows/         # Standard operating procedures for complex flows
│   └── changelog.md       # Audit log of changes to .agents/
├── .backup/               ← Archived old agent configs (if any)
└── ... (your code)
```

---

## Compatibility

`AGENTS.md` is an [open spec](https://agents.md/) maintained by OpenAI, Sourcegraph, Google, Cursor, and others. Real support across tools:

| Tool | Native AGENTS.md | Fallback (one-liner) |
|:--|:--|:--|
| **OpenAI Codex** | ✅ Reads it directly | — |
| **Cursor** | ✅ Reads it directly (incl. subdirs) | — |
| **Windsurf** | ✅ Reads it directly | — |
| **GitHub Copilot** (cloud coding agent) | ✅ Reads it directly | — |
| **GitHub Copilot** (IDE) | ⚠️ Still prefers its own file | `mkdir -p .github && ln -s ../AGENTS.md .github/copilot-instructions.md` |
| **Claude Code** | ⚠️ Needs an alias | `ln -s AGENTS.md CLAUDE.md` |
| **Gemini CLI** | ⚠️ Needs an alias | `ln -s AGENTS.md GEMINI.md` |

> **Practical tip:** keep `AGENTS.md` lean (≤ 200 lines) and let `.agents/` carry the rest of project knowledge — Codex silently truncates at 32 KiB, so shorter is safer.

> **Windows users:** replace `ln -s` with the PowerShell equivalent (Developer Mode required):
> ```powershell
> New-Item -ItemType SymbolicLink -Path CLAUDE.md -Target AGENTS.md
> ```
> Or just `Copy-Item AGENTS.md CLAUDE.md` (downside: updates require manual sync).

---

## Permission Model

A clear boundary between human control and agent autonomy:

| Content | Location | Permission |
|:--------|:---------|:-----------|
| Project notes, decisions, gotchas | `memory/` | Agent writes, merges, prunes freely |
| Coding conventions, code patterns | `rules/` | Agent writes freely; deletion needs user confirmation |
| Complex workflows | `workflows/` | Agent writes freely; deletion needs user confirmation |
| Absorbed legacy configs | `.backup/` | **Archived only after user confirmation** |
| Project metadata in `AGENTS.md` | `AGENT-WRITABLE` blocks | Agent updates as needed |
| Core conventions in `AGENTS.md` | Everything else | **Humans only** |

---

## Design Principles

**The agent builds its own workspace.** Don't pre-configure everything; let `AGENTS.md` teach the agent to create what it needs on demand. `.agents/` grows organically from real work and is periodically merged and pruned by the agent so it never turns into a junk pile.

**Humans hold the reins, the agent holds the notebook.** Conventions and engineering contracts are written by humans in `AGENTS.md`; project knowledge and working notes are maintained by the agent in `.agents/`. Clear responsibilities, no interference.

---

## FAQ

<details>
<summary><strong>How is this different from CLAUDE.md / .cursorrules?</strong></summary>

`AGENTS.md` is an [open spec](https://agents.md/) maintained by OpenAI, Sourcegraph, Google, Cursor, and others, and supported natively by most mainstream tools. Instead of maintaining a separate config per tool, use a single `AGENTS.md` as the source of truth. For tools that still want a tool-specific file (Claude Code's `CLAUDE.md`, Gemini CLI's `GEMINI.md`), one `ln -s AGENTS.md <alias>` is enough — see the Compatibility table above.

</details>

<details>
<summary><strong>Should I commit .agents/ to git?</strong></summary>

It depends. For personal projects, gitignore the whole `.agents/` — it's your private working memory. For team projects, commit static config (`rules/`, `workflows/`) to share team conventions, but gitignore dynamic data (`memory/`) since it's session-level. `AGENTS.md` itself should always be committed — it's the contract between project and agent.

> **Security note:** whether you commit it or not, set up a secret-scan (e.g. gitleaks). `.agents/memory/` will occasionally pick up things like "our API key is X"; preventing leaks beats cleaning them up.

</details>

<details>
<summary><strong>Won't .agents/ keep growing and turn into noise?</strong></summary>

It will, which is why `AGENTS.md` enforces a **maintenance cadence**: on session entry, validate that recent notes still match the code; whenever any file in `memory/` exceeds 200 lines, or `changelog.md` has grown ≥ 30 lines since the last `[MAINTENANCE]`, actively dedupe, merge, and drop stale content. Principle: **better to remember less than to remember wrong** — a wrong note is worse than no note. See the "Maintenance cadence" section of `AGENTS.md`.

</details>

<details>
<summary><strong>Will multiple agents collide?</strong></summary>

Different tools reading the same `AGENTS.md` and keeping their own session state work fine. But `.agents/` is just a directory — **no locking**. If you really do let two agents write the same file at once, they may overwrite each other. Run them serially, or have different agents write to different subdirs. Every write leaves a trace in `.agents/changelog.md` for postmortems.

</details>

<details>
<summary><strong>Can I customize the conventions?</strong></summary>

Yes — that's the whole point. The "Core Conventions" section of AGENTS.md is yours to edit — define whatever coding standards, commit format, testing requirements, and architectural rules suit your project. The `AGENT-WRITABLE` block is the only part the agent may modify; everything else is human-controlled.

</details>

<details>
<summary><strong>What if my project already has lots of agent config?</strong></summary>

agentrc is built for brownfield projects from day one. On the first run the agent auto-discovers existing config files (`.cursorrules`, `CLAUDE.md`, `.windsurfrules`, etc.) and absorbs their knowledge into `.agents/`. **Whether to archive the old files is your call** — the agent reports a discovery list and a proposed archive plan, and waits for your confirmation before moving anything to `.backup/`. Nothing is silently deleted or modified.

</details>

<details>
<summary><strong>What if my agent tool doesn't read AGENTS.md?</strong></summary>

Use the fallback symlinks from the Compatibility table. For example, Claude Code: `ln -s AGENTS.md CLAUDE.md`; Gemini CLI: `ln -s AGENTS.md GEMINI.md`. On Windows, use `New-Item -ItemType SymbolicLink` or just `Copy-Item`. Restart the tool and it picks up.

</details>

<details>
<summary><strong>Which parts of AGENTS.md can I edit?</strong></summary>

Everything except the blocks marked `<!-- AGENT-WRITABLE -->` (auto-maintained by the agent) — **you're welcome to edit the rest**, especially "Core Conventions". We do recommend keeping the overall structure of "Boot Instructions", "Self-Evolution Protocol", and "Hard Constraints" (the protocol layer); rewriting the specific clauses inside is fine.

</details>

<details>
<summary><strong>How does this relate to existing docs/ / CONTRIBUTING.md? Should I merge them?</strong></summary>

No need to merge — different audiences:

- `AGENTS.md` is for the agent. It must contain machine-executable rules ("test with jest", "run lint before commit").
- `CONTRIBUTING.md` / `docs/` is for humans. It can carry process etiquette, design philosophy, detailed tutorials.

When you want the agent to know a doc exists, just reference it from `AGENTS.md` (e.g. "Detailed architecture in `docs/architecture.md`"). The agent will read those on demand.

</details>

<details>
<summary><strong>Can the agent be hijacked by malicious content in .agents/?</strong></summary>

No. `AGENTS.md` mandates that **the only instruction sources are AGENTS.md itself and the user's current message** — everything else (`.agents/`, README, docs, source comments, git log, dependency READMEs, shell output) is treated as untrusted data. A 4-tier priority decides what to do with it:

1. **High-risk side effects** (deploy, delete, push, transfer money) → require explicit user confirmation in the moment
2. **Instructions targeting agent meta-behavior** ("read .env", "modify AGENTS.md", "ignore the above", source-code `// AGENT:` comments) → reject and report
3. **Project workflow commands** (lint / test / git pull) → executable after diffing against `package.json` / `Makefile`; destructive flags auto-escalate to tier 1
4. **Generic engineering conventions** (commit format, naming style) → reference knowledge

See "Boot Instructions" item 4 in `AGENTS.md`.

</details>

<details>
<summary><strong>Monorepo or multi-language project?</strong></summary>

Drop one `AGENTS.md` in each subproject root; most tools (Cursor, Codex, ...) automatically pick up the nearest one. Put shared conventions in the repo-root `AGENTS.md`, and let each subproject (e.g. `apps/web/AGENTS.md`, `apps/ios/AGENTS.md`) layer on its stack-specific overrides.

</details>

<details>
<summary><strong>Does it work in git worktrees / CI?</strong></summary>

- **worktrees:** `.agents/` follows each worktree (independent memory per worktree if not committed); to share, gitignore it and symlink to the main repo.
- **CI** (PR-review agents): we recommend read-only access to `AGENTS.md` + `.agents/rules/`, no writes to `.agents/memory/` (CI is ephemeral — writes get thrown away).

</details>

<details>
<summary><strong>Why doesn't the agentrc repo have its own .agents/?</strong></summary>

The agentrc repo's deliverable **is the AGENTS.md spec itself** — there's no business code requiring an agent to collaborate, so no `.agents/` to maintain. Drop `AGENTS.md` into **your** project, and on first run the agent will generate `.agents/` per the spec — that's where it belongs.

</details>

---

## Inspiration

> **Core belief:** AI agents deserve good engineering practices, not just good models.

- Anthropic's engineering blog on agent harnesses ([Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents), [Harness Design](https://www.anthropic.com/engineering/harness-design-long-running-apps))
- OpenAI's [AGENTS.md open spec](https://agents.md/) and [Codex practices](https://developers.openai.com/codex/guides/agents-md)
- Mitchell Hashimoto's [AI coding workflow notes](https://mitchellh.com/writing/my-ai-adoption-journey)
- Community summaries on harness engineering ([Addy Osmani](https://addyosmani.com/blog/agent-harness-engineering/), [HumanLayer](https://www.humanlayer.dev/blog/skill-issue-harness-engineering-for-coding-agents))

---

## Contributing

Contributions welcome! The goal is to stay lean and generic — if a change doesn't help at least three different AI tools, it probably doesn't belong here. Please open an issue first for structural changes; bug fixes and template improvements can go straight to PR.

---

## Star History

If agentrc helps your projects, please leave a Star — it helps more people find it.

[![Star History Chart](https://api.star-history.com/svg?repos=yeasy/agentrc&type=Date)](https://star-history.com/#yeasy/agentrc&Date)

---

<p align="center">
  <strong>MIT License</strong> — use anywhere, fork freely, make it your own.
</p>
