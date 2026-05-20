<h1 align="center">AgentGo</h1>

<p align="center">
  <strong>One AGENTS.md makes any project agent-ready.</strong>
</p>

<p align="center">
  <sub>Best practices baked in. No custom setup required.</sub>
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
  <img src="https://img.shields.io/github/license/yeasy/agentgo" alt="License">
</p>

---

## What It Solves

Models are already capable enough. What actually blocks product quality is **how agent-engineering best practices land in your own project** — and **you shouldn't have to research and configure that yourself**:

- Harness design, context management, memory upkeep, safety guardrails… top-tier practices are scattered across blog posts
- Claude Code / Codex / Cursor / Copilot / Windsurf / Gemini each have their own config format, and the same rules get rewritten over and over
- Once you do write down project conventions, the knowledge stays trapped in chat history; the longer the session, the more noise it accumulates

**What AgentGo gives you:** a stable [AGENTS.md protocol](https://raw.githubusercontent.com/yeasy/agentgo/main/AGENTS.md) plus an adaptive `.agents/` project layer. Drop `AGENTS.md` into any project root; the agent creates `.agents/` when project work needs adaptation or durable memory, records durable project knowledge after meaningful work, and never needs to edit `AGENTS.md` for that project.

|                          | Without AgentGo                                | With AgentGo                                          |
|:-------------------------|:-----------------------------------------------|:------------------------------------------------------|
| **Cross-tool reuse**     | One ruleset per tool, rewrite when you switch workspace | One `AGENTS.md` travels with the project, works everywhere |
| **Best practices**       | Scattered, re-researched per project           | Out of the box: conventions, flow, safety, upkeep cadence |
| **Self-improvement**     | Needs constant human reminders                 | Auto-learns and evolves — gets smarter over time      |
| **Project knowledge**    | Stuck in chat history, dies when the session ends | Persisted in `.agents/`, agent maintains and prunes itself |
| **Existing-doc adoption**| Agent configs and project docs scattered everywhere | Detect → index → extract; archive only obsolete files after you confirm |

---

## Getting Started

One step: download [AGENTS.md](https://github.com/yeasy/agentgo/blob/main/AGENTS.md) into your project root.

```bash
curl -fsSL https://raw.githubusercontent.com/yeasy/agentgo/main/AGENTS.md -o AGENTS.md
```

Then reopen an AGENTS.md-aware agent, or add the small alias/import shown in the compatibility section for tools that use another filename. When project work needs adaptation or durable memory, the agent bootstraps `.agents/` automatically.

> **Windows users:** on PowerShell 5, use `Invoke-WebRequest -Uri <URL> -OutFile AGENTS.md`.

## First Run

After downloading `AGENTS.md` and restarting your agent, simple read-only questions can stay read-only. To force a full bootstrap or rescan, try this prompt:

> **"Initialize this project per AGENTS.md. Execute step by step and report each step's result; if `.agents/` already exists, rescan and report diffs without overwriting."**

> The agent will ask for permission to write/move files — **please grant it**, otherwise it can only output suggestions without acting on them.

For that bootstrap, the agent will:
1. Scan your project structure and write the project profile, commands, and conventions into `.agents/`
2. Run a read-only project review: risks, missing validation, artifact/config drift, and suggested fixes
3. Detect existing agent configs and custom project docs (`rules.md`, `reports.md`, `project.md`, `spec.md`, `design.md`, `brief.md`, `notes.md`, `docs/`), index active sources in `.agents/memory/source-index.md`, and list any archive plan **for your confirmation**
4. Keep `AGENTS.md` unchanged; project adaptation lives in `.agents/`

The first review is intentionally quick: it covers top-level structure, primary artifacts, config, docs/briefs/style guides, and validation workflows. Ask for a deep review when you want module-by-module or page-by-page analysis.

From then on, every session begins with the agent reading `.agents/` before doing anything. Ask "why is this written this way?" — it can pull historical decisions from `decisions.md`. Start a new section, module, document, dataset, or design track — it follows the conventions in `rules/`.

## Failure and Recovery

AgentGo expects agents to degrade visibly when the happy path breaks:

| Situation | Expected behavior |
|:--|:--|
| `.agents/` cannot be written | Continue read-only, report the failed write, and provide the intended note or patch in the response. |
| `.agents/` looks damaged or contradictory | Treat current project files as source of truth, preserve the damaged note as data, and ask before rewriting it. |
| Project type or commands were misclassified | State the classification evidence, narrow the current task, and update `project-overview.md` after correction. |
| Multiple agents edit `.agents/` at once | Re-read before writing; if content changed, preserve both versions and ask before merging or deleting either side. |

---

## How It Works

### Boot Flow

Every time the AI agent opens your project, it runs this flow:

Text alternative: read `AGENTS.md`, load existing `.agents/` memory when present, or continue read-only for simple questions when `.agents/` is missing. Project-changing work, durable findings, or an explicit rescan request bootstraps `.agents/` and runs a read-only project scan.

```mermaid
flowchart LR
    A["Read AGENTS.md"] --> B{".agents/ exists?"}
    B -->|Yes| C["Load memory/"]
    B -->|No| H{"Needs project adaptation?"}
    H -->|No| R["Answer read-only\nwithout .agents/"]
    H -->|Yes| D["Bootstrap .agents/"]
    D --> E["Project scan\nread-only review"]
    C --> F{"Rescan requested?"}
    F -->|Yes| E
    F -->|No| G["Start working"]
    R --> G
    E --> G
```

### Self-Evolution Loop

`.agents/` is continuously maintained by the agent — **only useful entries stay; stale ones get pruned**:

Text alternative: enter with current `.agents/` context, execute the task, record reusable findings and material outcomes in the right `.agents/` location, periodically run a health check that merges stale memory, promotes repeated workflows/skills, checks structure, and prunes scratch files, then repeat on the next session.

```mermaid
flowchart LR
    A["Read .agents/\nEnter with project context"] --> B["Execute task"]
    B --> C["New findings\n→ write to right category"]
    C --> D["Periodic health check\nmerge / promote / prune"]
    D --> A

    style A fill:#1565C0,color:#fff
    style D fill:#B45309,color:#fff
```

New findings are filed by type: source document inventory → `memory/source-index.md`, project conventions → `rules/`, decisions → `memory/decisions.md`, gotchas → `memory/gotchas.md`, reusable patterns → `memory/patterns.md`, outcomes and user corrections → `memory/outcomes.md`, reusable workflows → `workflows/`, generated review reports → `reports/`, candidate workflows/skills → `experiments/`, current-task scratch output → `tmp/`, runtime-supported skills → `skills/` when useful, review findings → `memory/review-findings.md`, secret requirements without values → `memory/secret-requirements.md`, and unresolved work → `memory/open-items.md`. After each meaningful task, the agent records durable results and appends `.agents/changelog.md`. The maintenance cadence is enforced by `AGENTS.md` itself — **easy to write in, hard to stay** — so notes never pile up into noise.

Evolution is lifecycle-based: memory can be active, stale, deprecated, closed, or pinned; workflows and skills move from candidate to active to deprecated to archived. Health checks look for fitness signals such as fewer repeated mistakes, fewer user corrections, less stale context, higher validated reuse, and less repeated setup effort.

Recommended memory entry shape: `date`, `artifact`, `note`, `evidence`, `status`, and `next action`. The project does not need git; when no git repository exists, `.agents/changelog.md` still acts as the local audit trail.

### Validation Examples

| Project type | Typical validation |
|:--|:--|
| Code | test, build, lint, type check |
| Docs / slides | render/export, link check, style/consistency pass |
| Design | visual QA, export check, asset inspection |
| Data | schema check, recalculation, sample validation |
| Research | source quality, date check, citation coverage |

### Brownfield Auto-Adoption

If your project already has `.cursorrules` / `CLAUDE.md` / `.windsurfrules` / `.github/copilot-instructions.md`, custom docs such as `rules.md` / `reports.md` / `project.md`, docs, briefs, style guides, design notes, data dictionaries, or workflow files scattered around, the agent will, during bootstrap or explicit rescan:

1. Scan existing agent configs and project reference docs
2. Index active source files in `.agents/memory/source-index.md`
3. Extract reusable knowledge into `.agents/`
4. List a discovery report and any proposed archive plan
5. **Wait for your nod** before moving obsolete or duplicate files

Active human-facing docs stay where they are. Archive agent-specific legacy files under `.agents/archive/`, and human-facing docs only in the project's normal docs archive location, such as `docs/archive/`. Avoid a generic `.bak/` directory because it hides intent. Nothing is lost; every archive action requires your confirmation.

### Directory Layout

After a few sessions, your project ends up like this:

```
your-project/
├── AGENTS.md              ← The only file you add (human-controlled)
├── .agents/               ← Auto-created when project work needs memory
│   ├── memory/            # Project overview, decisions, findings, open items
│   ├── rules/             # Project conventions extracted from artifacts/config
│   ├── workflows/         # Standard operating procedures for recurring flows
│   ├── reports/           # Generated review reports, not committed by default
│   ├── experiments/       # Candidate workflows/skills before promotion
│   ├── tmp/               # Scratch/intermediate files, pruned automatically
│   ├── skills/            # Optional repo-scoped skills for supporting runtimes
│   ├── archive/           # Obsolete agent-only configs, only after confirmation
│   └── changelog.md       # Audit log of changes to .agents/
├── docs/archive/          ← Optional human-doc archive, only if the project uses it
└── ... (your project files)
```

---

## Compatibility

`AGENTS.md` is an [open format](https://agents.md/) that emerged from collaboration across the AI agent ecosystem and is now stewarded by the Agentic AI Foundation. Real support across tools:

| Tool | How to use AgentGo |
|:--|:--|
| **OpenAI Codex** | Reads repository `AGENTS.md` instructions. |
| **GitHub Copilot coding agent** | Reads the nearest `AGENTS.md` in the repository tree. |
| **Claude Code** | Reads `CLAUDE.md`; create `CLAUDE.md` with `@AGENTS.md` or symlink it. |
| **Cursor** | Reads a project-root `AGENTS.md` as a simple always-on instruction file; use `.cursor/rules/` when you need richer metadata or scoped rules. |
| **Windsurf** | Automatically discovers `AGENTS.md` / `agents.md`; root files are always-on and nested files apply by directory scope. |
| **Gemini CLI** | Defaults to `GEMINI.md`; configure `context.fileName` to include `AGENTS.md`, import it, or symlink it. |
| **Other AGENTS.md ecosystem tools** | Check the tool's docs; many can read `AGENTS.md` directly or through a filename setting. |

> **Practical tip:** keep `AGENTS.md` lean (around 200 lines) and let `.agents/` carry project-specific knowledge.

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
| Outcome ledger and user corrections | `memory/outcomes.md` | Agent records material results and feedback |
| Project conventions and reusable patterns | `rules/` | Agent writes freely; deletion needs user confirmation |
| Complex workflows | `workflows/` | Agent writes freely; deletion needs user confirmation |
| Generated review reports and visual diffs | `reports/` | Agent writes freely; not committed by default |
| Experiments and candidate skills/workflows | `experiments/` | Agent writes freely; deletion needs user confirmation |
| Scratch/intermediate files | `tmp/` | Agent writes and prunes freely; not committed |
| Runtime-supported skills | `skills/` | Optional focused workflows; deletion needs user confirmation |
| Source document inventory | `.agents/memory/source-index.md` | Agent indexes active project references |
| Secret requirements | `.agents/memory/secret-requirements.md` | Names, sources, scopes, and owners only; no secret values |
| Obsolete agent-only configs | `.agents/archive/` | **Archived only after user confirmation** |
| Obsolete human-facing docs | Project docs archive, e.g. `docs/archive/` | **Archived only after user confirmation** |
| Project metadata, review findings, and memory | `.agents/` | Agent creates when first needed and updates after meaningful work |
| Stable protocol | `AGENTS.md` | **Humans only**, unless the user explicitly asks to edit AGENTS.md |

---

## Design Principles

**The agent builds its own workspace.** Don't pre-configure everything; let `AGENTS.md` teach the agent to create what it needs on demand. `.agents/` grows organically from real work and is periodically merged and pruned by the agent so it never turns into a junk pile.

**Humans hold the reins, the agent holds the notebook.** Conventions and engineering contracts are written by humans in `AGENTS.md`; project knowledge and working notes are maintained by the agent in `.agents/`. Clear responsibilities, no interference.

---

## FAQ

<details>
<summary><strong>How is this different from CLAUDE.md / .cursorrules?</strong></summary>

`AGENTS.md` is an [open format](https://agents.md/) for agent instructions. Instead of maintaining a separate ruleset per tool, use one stable `AGENTS.md` as the protocol and keep project-specific memory in `.agents/`. For tools that use a different filename, import or symlink `AGENTS.md` — see the Compatibility table above.

</details>

<details>
<summary><strong>Should I commit .agents/ to git?</strong></summary>

It depends. For personal projects, gitignore the whole `.agents/` — it's your private working memory. For team projects, commit static config (`rules/`, `workflows/`, optionally `skills/`) to share team conventions, but gitignore dynamic data (`memory/`) since it's session-level. `AGENTS.md` itself should always be committed — it's the contract between project and agent.

Common team pattern:
```gitignore
.agents/memory/
.agents/changelog.md
```

> **Security note:** whether you commit it or not, set up a secret-scan (e.g. gitleaks). `.agents/memory/` will occasionally pick up things like "our API key is X"; preventing leaks beats cleaning them up.

</details>

<details>
<summary><strong>How do I update AGENTS.md later?</strong></summary>

Update only `AGENTS.md`; keep `.agents/` in place. `.agents/` is your project's local memory and should not be deleted or replaced during template updates.

Keep the same language variant you installed. English projects should update from `AGENTS.md`; Simplified Chinese installs should update from `AGENTS.zh-CN.md`, still saved locally as `AGENTS.md`.

If your local `AGENTS.md` has no project-specific edits:

```bash
curl -fsSL https://raw.githubusercontent.com/yeasy/agentgo/main/AGENTS.md -o AGENTS.md
```

If you may have edited it locally, diff before replacing:

```bash
curl -fsSL https://raw.githubusercontent.com/yeasy/agentgo/main/AGENTS.md -o /tmp/AGENTS.latest.md
diff -u AGENTS.md /tmp/AGENTS.latest.md
```

To pin a stable release instead of tracking `main`:

```bash
curl -fsSL https://raw.githubusercontent.com/yeasy/agentgo/v1.0.0/AGENTS.md -o AGENTS.md
```

Do not let an agent silently replace `AGENTS.md` on a timer. During `.agents/` maintenance, it may check for a newer AgentGo template and suggest an update, but replacement should still require your explicit request or approval. The first comment in `AGENTS.md` carries the template version, for example `AGENTS.md v1.3.0`; release tags are the stable install target.

After updating, restart or rescan your agent:

> **"Rescan this project per AGENTS.md. Keep the existing `.agents/`; report new or changed guidance without overwriting memory."**

</details>

<details>
<summary><strong>Won't .agents/ keep growing and turn into noise?</strong></summary>

It will, which is why `AGENTS.md` enforces a **maintenance cadence**: on session entry, validate that recent notes still match current project artifacts; run a health check whenever any `memory/` file exceeds 200 lines, `changelog.md` has grown ≥ 30 lines since the last `[MAINTENANCE]`, 10 meaningful tasks have completed, stale notes are found, `.agents/` structure drifts, or `tmp/` contains stale scratch output. Maintenance dedupes entries, closes resolved items, removes stale notes, records fitness signals, promotes repeated validated procedures into `workflows/` or supported `skills/`, prunes `tmp/`, and can generate `reports/health-<date>.md` for non-trivial cleanups.

</details>

<details>
<summary><strong>Will the agent proactively suggest improvements?</strong></summary>

Yes, but only as optional follow-up. When the agent has clear evidence that an out-of-scope improvement would likely help, it should briefly explain the suggestion, rationale, and risk, then wait. It should not execute optional suggestions without your request, and it should not distract you with low-confidence ideas.

</details>

<details>
<summary><strong>Will multiple agents collide?</strong></summary>

Different tools reading the same `AGENTS.md` and keeping their own session state work fine. But `.agents/` is just a directory — **no locking**. If you really do let two agents write the same file at once, they may overwrite each other. Run them serially, or have different agents write to different subdirs. Every write leaves a trace in `.agents/changelog.md` for postmortems.

</details>

<details>
<summary><strong>Can I customize the conventions?</strong></summary>

Yes — as a human-maintained protocol. The default AgentGo design is that agents do not rewrite `AGENTS.md` during project adaptation; they write project-specific findings into `.agents/`. If you want different universal rules, edit `AGENTS.md` directly.

</details>

<details>
<summary><strong>What if my project already has lots of agent config?</strong></summary>

AgentGo is built for brownfield projects from day one. During bootstrap or rescan, the agent discovers existing config files (`.cursorrules`, `CLAUDE.md`, `.windsurfrules`, etc.) and custom project docs (`rules.md`, `reports.md`, `project.md`, `spec.md`, `design.md`, `brief.md`, `notes.md`, and similar). Active docs stay in place and are indexed in `.agents/memory/source-index.md`; reusable knowledge is extracted into `.agents/`. **Whether to archive obsolete files is your call** — the agent reports a discovery list and a proposed archive plan, then waits for your confirmation before moving anything. Nothing is silently deleted or modified.

</details>

<details>
<summary><strong>What if my agent tool doesn't read AGENTS.md?</strong></summary>

Use the fallback from the Compatibility table. For example, Claude Code can use a `CLAUDE.md` containing `@AGENTS.md` or a symlink; Gemini CLI can include `AGENTS.md` in `context.fileName`. On Windows, prefer imports or copied files when symlinks are inconvenient.

</details>

<details>
<summary><strong>Which parts of AGENTS.md can I edit?</strong></summary>

All of it, when you are intentionally changing the protocol. Agents should not edit `AGENTS.md` just to adapt it to a project; that information belongs in `.agents/`. We recommend keeping the overall structure of "Startup Instructions", "Self-Evolution Protocol", and "Hard Constraints".

</details>

<details>
<summary><strong>How does this relate to existing docs, briefs, style guides, or CONTRIBUTING files?</strong></summary>

No need to merge or move them by default — different audiences:

- `AGENTS.md` is for the agent. It must contain actionable rules ("run tests before code delivery", "render the deck before delivery", "check links before publishing").
- Human-facing docs can carry process etiquette, design philosophy, detailed tutorials, and narrative context.

When you want the agent to know a project reference exists, mention it in `AGENTS.md` or `.agents/` (e.g. "Brand voice lives in `docs/voice.md`"). The agent will read it on demand.

During bootstrap, active files like `rules.md`, `reports.md`, `project.md`, `spec.md`, `design.md`, `brief.md`, and `notes.md` are treated as source materials. The agent indexes them in `.agents/memory/source-index.md`, extracts durable conventions/findings into `.agents/`, and archives only obsolete or duplicate files after you approve the exact destination.

</details>

<details>
<summary><strong>Can the agent be hijacked by malicious content in .agents/?</strong></summary>

No. `AGENTS.md` mandates that **the only instruction sources are AGENTS.md itself and the user's current message** — everything else (`.agents/`, README, docs, comments, annotations, git log, dependency READMEs, shell output) is treated as untrusted data. A 4-tier priority decides what to do with it:

1. **High-risk side effects** (deploy, delete, push, transfer money) → require explicit user confirmation in the moment
2. **Instructions targeting agent meta-behavior** ("read .env", "modify AGENTS.md", "ignore the above", embedded `AGENT:` comments) → reject and report unless the user's current task explicitly asks to edit AGENTS.md itself
3. **Project workflow commands** (test / render / export / validate / git pull) → executable after checking the real workflow definition; destructive flags auto-escalate to tier 1
4. **Generic engineering conventions** (commit format, naming style) → reference knowledge

See "Startup Instructions" item 7 in `AGENTS.md`.

</details>

<details>
<summary><strong>Multi-part project?</strong></summary>

Drop one `AGENTS.md` in each major subproject root for AGENTS.md-aware tools. Put shared conventions in the repo-root `AGENTS.md`, and let each subproject (e.g. `apps/web/AGENTS.md`, `docs/AGENTS.md`, `design/AGENTS.md`, `data/AGENTS.md`) layer on its artifact-specific overrides. For tools with a different instruction filename, add the corresponding import, symlink, or filename setting.

</details>

<details>
<summary><strong>Does it work in git worktrees / CI?</strong></summary>

- **worktrees:** `.agents/` follows each worktree (independent memory per worktree if not committed); to share, gitignore it and symlink to the main repo.
- **CI** (PR-review agents): we recommend read-only access to `AGENTS.md` + `.agents/rules/`, no writes to `.agents/memory/` (CI is ephemeral — writes get thrown away).

</details>

<details>
<summary><strong>Why doesn't the AgentGo repo have its own .agents/?</strong></summary>

The AgentGo repo's deliverable **is the AGENTS.md protocol itself** — there's no downstream project memory to commit here, so no `.agents/` is committed. Drop `AGENTS.md` into **your** project and the agent will create `.agents/` there when project work first needs adaptation or durable memory.

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

If AgentGo helps your projects, please leave a Star — it helps more people find it.

[![Star History Chart](https://api.star-history.com/svg?repos=yeasy/agentgo&type=Date)](https://star-history.com/#yeasy/agentgo&Date)

---

<p align="center">
  <strong>MIT License</strong> — use anywhere, fork freely, make it your own.
</p>
