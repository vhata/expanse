# AGENTS.md

Expanse is a text snippet manager for macOS: a Click CLI (`expanse`) over a JSON file at `~/.expanserc`, used from a Hammerspoon chooser and, optionally, a rumps menu-bar daemon. Structure and invariants are in [ARCHITECTURE.md](ARCHITECTURE.md); gates and test policy in [docs/QUALITY.md](docs/QUALITY.md); past choices in [docs/DECISIONS.md](docs/DECISIONS.md).

<!-- docket:begin -->

## Docket

This project is run with docket. Read [docket/CONTRACT.md](docket/CONTRACT.md) before any work; it is the authoritative workflow, and this section records only this project's settings. The installer keeps this section current: the text above the list is rewritten on every run, the list keeps the values this project has set, and the section may sit anywhere in this file.

- Queue areas: `[CLI]`, `[CORE]`, `[GUI]` (rumps daemon and the Hammerspoon integration), `[TOOLING]`, `[DOCS]`.
- Concurrency cap: none; the suite is small and runs in seconds.
- Merging and releases: the user merges unless delegated in the turn. There are no releases or published packages.
- Optional pieces in force: review ledger (installed, no review recorded yet). Deferred: roadmap queue, stacked PRs, scheduled validation of main.
- Environment: run Python through the worktree's `.venv/`, created from Python 3.12 by `bash scripts/setup.sh`; never install into a global interpreter. Tests must never read or write the real `~/.expanserc`. The user runs the GUI daemon and Hammerspoon themselves; the Hammerspoon config lives outside this repository at `~/.hammerspoon/expanse.lua`.
- Git identity: commits use `jonathan.hitchcock@gmail.com` (personal project), set in the clone's local config.

<!-- docket:end -->
