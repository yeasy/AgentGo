# AgentGo Protocol Conformance Corpus

This directory contains a machine-readable protocol conformance corpus for AgentGo. It turns a small set of safety and continuity rules into reference fixtures plus expected and forbidden normalized observations.

It is not a cross-tool benchmark and does not claim that any agent or tool passes. A tool-specific runner must execute each scenario, normalize its trace into the declared event vocabulary, and publish evidence before making a compatibility claim.

## Schema

`scenarios.json` records the corpus and protocol versions, runner safety contract, deterministic session ID, event vocabulary, and scenarios. Each scenario has bilingual prompts, references to both protocol variants, an isolated fixture, and non-empty `expected` and `forbidden` observations. Observation targets use POSIX-style glob patterns when a runner needs to match a family of paths or effects.

## Runner safety

Runners must preserve the declared defaults: isolated temporary repository, network disabled, external side effects stubbed, and synthetic secrets only. Fixtures describe simulated state; they are not instructions to access a developer's real workspace, credentials, network, or remote services.

## Observation contract

A scenario passes only when every `expected` event is observed at least once and every `forbidden` event is absent. Runners are responsible for mapping tool-specific calls and responses to the corpus vocabulary without weakening the target meaning.

The corpus validates scenario structure and protocol provenance. It does not prove that natural-language behavior is deterministic, that all edge cases are covered, or that two tools interpret an event identically.

## Validation

Run the repository's standard contract suite:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```
