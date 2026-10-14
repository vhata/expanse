# Review backlog

Only work promoted from whole-codebase reviews belongs here. Every entry is ready for separate work and carries a `Findings:` line naming the raw review findings it covers; each finding maps to at most one entry. Claiming and resolving follow [docket/TODO_GUIDE.md](../docket/TODO_GUIDE.md); promotion follows [docket/CODE_REVIEW_GUIDE.md](../docket/CODE_REVIEW_GUIDE.md).

## P0 Critical

## P1 High

## P2 Normal

- [CORE] `core-validates-store` — **`expanse/core.py` validates the whole store in one place and raises a store error that every caller handles.** Today `load_expansions` turns a parse error into an empty store, only the CLI validates first, other malformed shapes and I/O errors end in tracebacks, and non-string values reach `get` and `dump`.
  - Source: review/2026-10-12-1703-full.md, 2026-10-12
  - Findings: `load-swallows-malformed-store`, `store-shape-unvalidated`, `get-prints-non-string-values`
  - Starting point: one validator for "a dict with an `expansions` dict of string to string", catching `OSError` and `ValueError`, shared by `load_expansions` and `ensure_expfile`; the CLI reports it through the existing "Could not access" path.
  - Related: `daemon-guards-malformed-store`, `edit-abort-keeps-content`, `test-malformed-store-abort`

## P3 Low

- [CLI] `cli-input-fidelity` — **`add` and `edit` store exactly what the user gave and reject names that would break the `dump` format.** A name containing a newline shifts every later entry in the Hammerspoon chooser, and `add` without `-e` strips leading indentation.
  - Source: review/2026-10-12-1703-full.md, 2026-10-12
  - Findings: `dump-name-newline-breaks-pairs`, `add-stdin-strips-whitespace`
  - Starting point: `expanse/cli.py` `add` and `edit`; also state the single-line name rule under Shared interfaces in `ARCHITECTURE.md`.
  - The `dump` and `get` output is pinned by CliRunner tests in `tests/test_expanse.py`; a change to either must update them and `~/.hammerspoon/expanse.lua` in step.
- [CORE] `private-store-permissions` — **`~/.expanserc` is created and rewritten with mode 0600.** It is created 0644 under the default umask, and macOS home directories are group-readable by `staff`.
  - Source: review/2026-10-12-1703-full.md, 2026-10-12
  - Findings: `store-world-readable`
  - Starting point: `expanse/core.py` `save_expansions` and `ensure_expfile`; take it with `atomic-save`, which rewrites the same function.
  - Related: `atomic-save`

## Unprioritized
