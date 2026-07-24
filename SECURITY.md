# Security Policy

AgentGo is a text protocol: the deliverable is `AGENTS.md` itself. A "vulnerability" here is usually a protocol-level weakness — wording that lets untrusted content gain instruction authority (prompt-injection laundering), permission rules that contradict each other, or unsafe defaults in the documented install/update flows.

## Reporting

- For protocol weaknesses, ambiguities, or unsafe defaults that carry no immediate exploitation risk, open a regular [GitHub issue](https://github.com/yeasy/agentgo/issues).
- For anything you would not want public before a fix lands (for example a realistic injection chain against downstream users), use [GitHub private vulnerability reporting](https://github.com/yeasy/agentgo/security/advisories/new).

Please cite the exact file and line plus a concrete misuse scenario. Expect an initial response within a week.

## Scope and expectations

- The protocol's trust tiers are best-effort heuristics, not a guaranteed boundary — `AGENTS.md` states this explicitly. A report that text rules cannot stop prompt injection in general is already acknowledged; what helps is a *specific* wording flaw with a suggested fix direction.
- Runtime enforcement (permissions, sandboxing, network controls) belongs to the agent tools themselves; please report tool bugs upstream to the respective projects.
- The supported version is the latest release tag. Pinned older installs should update via the flow described in the README FAQ.
