# Review backlog

Only work promoted from whole-codebase reviews belongs here. Every entry is ready for separate work and carries a `Findings:` line naming the raw review findings it covers; each finding maps to at most one entry. Claiming and resolving follow [docket/TODO_GUIDE.md](../docket/TODO_GUIDE.md); promotion follows [docket/CODE_REVIEW_GUIDE.md](../docket/CODE_REVIEW_GUIDE.md).

## P0 Critical

## P1 High

## P2 Normal

- [CORE] `transactional-cli-writes` — **Interactive CLI writes preserve unrelated concurrent updates and report conflicts.** Commands retain a full store snapshot while waiting for an editor, stdin or confirmation, then replace newer state with it.
  - Source: review/2026-10-27-1619-full.md, 2026-10-27
  - Findings: `cli-interactive-save-loses-updates`
  - Starting point: `expanse/cli.py` `edit` and `add`, and the storage mutation boundary in `expanse/core.py`; validate current state and serialize read-modify-write operations rather than only reloading before a write.
  - Acceptance: while an edit is open, a second CLI add survives the edit save; a same-key change or externally malformed replacement is reported without overwriting it. Include deterministic two-writer checks and retain CLI output contracts.

## P3 Low

- [CLI] `cli-input-fidelity` — **`add` and `edit` preserve explicit input and reject names that would break the `dump` format.** A newline name shifts later chooser entries, stdin loses indentation, and explicit `-e ''` incorrectly consumes stdin.
  - Source: review/2026-10-12-1703-full.md, 2026-10-12
  - Findings: `dump-name-newline-breaks-pairs`, `add-stdin-strips-whitespace`, `add-empty-option-reads-stdin`
  - Additional source: review/2026-10-27-1619-full.md, 2026-10-27
  - Starting point: `expanse/cli.py` `add` and `edit`; also state the single-line name rule under Shared interfaces in `ARCHITECTURE.md`.
  - The `dump` and `get` output is pinned by CliRunner tests in `tests/test_expanse.py`; a change to either must update them and `~/.hammerspoon/expanse.lua` in step.
- [CORE] `private-store-permissions` — **`~/.expanserc` is created and rewritten with mode 0600.** It is created 0644 under the default umask, and macOS home directories are group-readable by `staff`.
  - Source: review/2026-10-12-1703-full.md, 2026-10-12
  - Findings: `store-world-readable`
  - Starting point: `expanse/core.py`: `_replace_with_json`, through which `save_expansions` writes, keeps an existing file's mode and gives a new one `0o666 & ~umask`; `ensure_expfile` creates a missing store with `open("x")`. Both need the 0600 mode.

- [GUI] `daemon-commit-after-save` — **Failed daemon writes leave the cache and menu at the last saved state.** Mutations currently stay copyable after a write error and are persisted by a later unrelated action.
  - Source: review/2026-10-27-1619-full.md, 2026-10-27
  - Findings: `daemon-failed-save-keeps-mutation`
  - Starting point: `expanse/daemon.py` mutation handlers and `save_expansions`; return the save outcome and publish candidate state only on success.
  - Acceptance: force add, edit and delete writes to fail; disk, menu and copied values stay unchanged, and a later successful action never commits the failed mutation.

## Unprioritized
