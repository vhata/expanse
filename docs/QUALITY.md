# Quality and validation

Read when changing code or preparing a PR. This document describes the gates as they exist now; history and rationale for past changes live in `docs/DECISIONS.md` and git.

## What quality means here

- The snippet store is the user's data: no command may lose or corrupt `~/.expanserc`, and a malformed file is reported rather than overwritten.
- The CLI output that the Hammerspoon integration parses stays stable (see [Shared interfaces](../ARCHITECTURE.md#shared-interfaces)).
- The GUI daemon and the Hammerspoon chooser are checked by hand on macOS; no automated test drives them.

## Gates

Each check is a standalone script in `scripts/` or `docket/scripts/`, runnable from any directory, exiting non-zero on failure. Hooks, CI and agents run the same scripts. The gate scripts use the worktree's `.venv/` and fail with a pointer to `bash scripts/setup.sh` when it is missing.

| Script | Runs | Pre-commit | Pre-push | CI on PR | CI on main | Scheduled |
| --- | --- | --- | --- | --- | --- | --- |
| `scripts/fmt-check.sh` | `ruff format --check` | yes (staged files) | | yes | yes | |
| `scripts/lint.sh` | `ruff check`, any finding fails | yes (staged files) | | yes | yes | |
| `scripts/test.sh` | `pytest --strict-markers`; empty collection fails | | yes | yes | yes | |
| `docket/scripts/ci.sh` | queue hygiene, Markdown links, PR markers against the queues | | | yes | yes | |
| `scripts/check.sh` | fmt-check, lint, test, in order | | | yes | yes | |

`scripts/check.sh` is the composite entry point: `ci.yml` runs it rather than the gates individually, so its CI columns are those of the gates it runs. `scripts/format.sh` is the write-mode formatter. There is no type checker gate yet (`add-typecheck-gate` in `TODO.md`).

Hooks live in the tracked `.githooks/` directory and are wired by `bash scripts/setup.sh` through `git config core.hooksPath .githooks`. Pre-commit checks only, against the staged content of staged Python files, and never rewrites files. Bypassing a hook is for a broken toolchain only; state the bypass and the equivalent checks in the PR.

Toolchain pins: `.python-version` (3.12), `requirements-dev.txt` (pytest, pytest-mock, pyfakefs, ruff), `ruff.toml` (rule set). Runtime dependencies in `setup.py` are not pinned. Bumping a pin is its own PR.

Known state: `main` fails `fmt-check`, `lint` and `test` on code that predates these gates. `fix-broken-tests` and `ruff-baseline` in `TODO.md` make it green.

## Test policy

- A behaviour change or bug fix in `expanse/core.py` or `expanse/cli.py` comes with a test through `click.testing.CliRunner` or the core functions directly.
- Tests isolate the snippet store with pyfakefs or a temporary `$HOME`; they never touch the real `~/.expanserc`.
- Changes to `expanse/daemon.py` and the Hammerspoon-facing output are verified by hand on macOS; the PR states the scenario run.
- An empty or skipped suite is a failed gate. There is no coverage gate.
- No automatic retries. A flaky test is filed in `TODO.md` with its output and fixed or quarantined by name.

## Review inputs

Read by `docket/CODE_REVIEW_GUIDE.md`, which links this section by its heading, so keep the heading as it is; a codebase review runs and records exactly what is listed here.

- Focus areas: the correctness boundaries under [What quality means here](#what-quality-means-here) and the invariants in [ARCHITECTURE.md](../ARCHITECTURE.md).
- Baseline commands beyond `bash scripts/check.sh`: `HOME=$(mktemp -d) .venv/bin/expanse dump` and `HOME=$(mktemp -d) .venv/bin/expanse get -- missing; echo $?` (record output and exit status; both should be empty output and status 0).
- Drift checks for an incremental review: `README.md`, `CLAUDE.md` and the CLI section of `ARCHITECTURE.md` against `expanse/cli.py`; the CLI output against `~/.hammerspoon/expanse.lua` where the reviewer can read it; this document against `.githooks/` and `.github/workflows/`; `noqa` counts.
- Source paths for `bash docket/scripts/review-due.sh --paths "expanse tests"`.
- Expected tracked files: `*.py`, `*.md`, `*.sh`, `*.txt`, `*.toml`, `*.yml`, `*.plist`, `.githooks/*`, `.python-version`, `.gitignore`, `LICENSE.txt`, and `docket/` as vendored.

## CI

`.github/workflows/ci.yml` runs on pull requests and on pushes to `main`. Jobs: `check` (macOS; `scripts/setup.sh` then `scripts/check.sh`) and `Queue and PR hygiene` (Ubuntu; `bash docket/scripts/ci.sh`). On pull requests the marker check compares the queues at the base branch tip with the checked-out merge commit. Superseded runs are cancelled on PR branches only, never on `main`. No failure evidence is uploaded; the job log is the evidence.

## Scheduled validation of main

Deferred (see `docs/DECISIONS.md`). A red `main` from the push run is reverted or filed as a P1 the same day.

## Branch protection

Not configured: `main` accepts direct pushes, no checks are required, and merge commits, rebase and squash merges are all allowed. Update this section with the settings and the date when protection is applied.

## PR evidence

Every PR lists the commands run and their results, a reproducible scenario for behaviour changes, what was not run and why, and the independent review. See [docket/CODE_REVIEW_GUIDE.md](../docket/CODE_REVIEW_GUIDE.md).
