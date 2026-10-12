# Deferred work

Ordinary follow-ups and bugs found during other work live here. Whole-codebase review findings promoted for separate work live in [review/BACKLOG.md](review/BACKLOG.md). Follow [docket/TODO_GUIDE.md](docket/TODO_GUIDE.md) before adding, claiming, moving or resolving an entry. Entries in **Ready for separate work** are unblocked and available now; anything with an unresolved `Depends on:` belongs in an earlier stage.

## Needs triage

### P0 Critical

### P1 High

### P2 Normal

### P3 Low

### Unprioritized

- [CLI] `test-malformed-store-abort` — **A CLI command against a malformed store exits non-zero and leaves the file unchanged.** The group's `ensure_expfile` check in `expanse/cli.py` aborts on a malformed store, which is how the CLI keeps the "a malformed file is reported rather than overwritten" invariant, but no test covers it: replacing the check with `if False:` leaves the suite green.
  - Source: independent review of todo/fix-broken-tests (#2), 2026-10-12
  - Starting point: a test in `tests/test_expanse.py` using the `expfile` fixture with invalid JSON, invoking `add`, and asserting a non-zero exit and the original contents.
- [TOOLING] `drop-pytest-mock` — **`requirements-dev.txt` pins only what the suite uses.** The tests stopped using `pytest-mock` when they moved to pyfakefs and a fake `$HOME`, but it is still pinned and listed in `docs/QUALITY.md`.
  - Source: independent review of todo/fix-broken-tests (#2), 2026-10-12
  - Starting point: remove the pin from `requirements-dev.txt` and the mention in `docs/QUALITY.md`; a pin change is its own PR.
- [CLI] `edit-abort-keeps-content` — **Quitting the editor without saving leaves the snippet unchanged.** `click.edit` returns `None` when the editor exits without saving, and `expanse edit` stores that, replacing the content with `null`; `expanse dump` then crashes with `AttributeError`, which empties the Hammerspoon chooser.
  - Source: independent review of task/adopt-docket, 2026-10-11
  - Evidence: `HOME=$(mktemp -d) EDITOR=true expanse edit -n z` leaves `{"expansions": {"z": null}}`.
  - Starting point: `expanse/cli.py`, `edit`.
- [GUI] `daemon-reloads-store` — **The daemon never overwrites snippets added elsewhere while it runs.** It loads the store once at startup and saves its in-memory copy on every change, so anything the CLI or Hammerspoon added since startup is lost on the next daemon save.
  - Source: independent review of task/adopt-docket, 2026-10-11
  - Starting point: `expanse/daemon.py`; reload before each mutation. Found by reading the code, not reproduced.
  - Related: `daemon-guards-malformed-store`, `atomic-save`
- [GUI] `fix-daemon-entry-points` — **`run.sh` and `python -m expanse.daemon` start the daemon.** `run.sh` runs `python3 expanse/daemon.py`, which fails on the relative import `from .core`; `python -m expanse.daemon` (in `CLAUDE.md`) exits silently because no module has a `__main__` guard.
  - Source: independent review of task/adopt-docket, 2026-10-11
  - Related: `fix-daemon-install`
  - Also: `run.sh` is tracked as mode 100644, so `./run.sh` fails with permission denied before reaching the import error. Source: review/2026-10-12-1703-full.md, 2026-10-12
- [CORE] `atomic-save` — **Saving snippets cannot truncate `~/.expanserc` if the process dies mid-write.** `save_expansions` opens the store with mode `w` and writes in place, so an interrupted write leaves an empty or partial file.
  - Source: task/adopt-docket inspection, 2026-10-11
  - Starting point: write to a temporary file in the same directory and `os.replace` it.
- [GUI] `daemon-guards-malformed-store` — **The daemon refuses to save over a store it could not parse.** `load_expansions` returns an empty store on a JSON error; the CLI checks `ensure_expfile` first, but `expanse/daemon.py` loads and saves directly, so one add from the menu would replace a malformed file with a single snippet.
  - Source: task/adopt-docket inspection, 2026-10-11
- [GUI] `fix-daemon-install` — **`install.sh` and `com.expanse.daemon.plist` install the daemon that actually exists, or are removed.** Both reference `expanse_daemon.py`, which is not in the repository; the daemon is now the `expanse-gui` entry point.
  - Source: task/adopt-docket inspection, 2026-10-11
  - Also: `install.sh` installs with `pip3` into the global interpreter, and the plist's `KeepAlive` would make launchd retry the missing path indefinitely. Source: review/2026-10-12-1703-full.md, 2026-10-12
- [TOOLING] `fix-setup-metadata` — **`setup.py` declares the real dependencies and owner.** It lists `pynput`, which no code imports, omits `rumps` and `pyperclip`, which the daemon needs (they are only in `pip-requirements.txt`), and carries placeholder author, email and URL.
  - Source: task/adopt-docket inspection, 2026-10-11
  - Related: `adopt-pyproject-lock`
  - Also: `find_packages()` has no exclude, so `tests` is installed as a top-level package (see `expanse.egg-info/top_level.txt`), and `python_requires=">=3.6"` and the "OS Independent" classifier disagree with a 3.12-only, macOS-only project. Source: review/2026-10-12-1703-full.md, 2026-10-12
- [TOOLING] `untrack-egg-info` — **`expanse.egg-info/` is ignored rather than tracked.** It is build output that `pip install -e .` regenerates in place.
  - Source: task/adopt-docket inspection, 2026-10-11
- [TOOLING] `adopt-pyproject-lock` — **Packaging moves to `pyproject.toml` with a lockfile, and `scripts/setup.sh` installs from it exactly.** Runtime dependencies are unpinned today and dependencies are split across `setup.py`, `pip-requirements.txt` and `requirements-dev.txt`.
  - Source: task/adopt-docket inspection, 2026-10-11
  - Related: `fix-setup-metadata`
- [TOOLING] `add-typecheck-gate` — **A type checker runs as `scripts/typecheck.sh` in `scripts/check.sh`, the pre-push hook and CI.** The code is partly annotated and nothing checks the annotations.
  - Source: task/adopt-docket inspection, 2026-10-11
- [DOCS] `refresh-readme` — **`README.md` describes the CLI and the Hammerspoon integration as they work today.** It presents the daemon as the main interface, names an `expanse-daemon` command that does not exist and gives the hotkey as Ctrl+Alt+E (Hammerspoon uses Cmd+Alt+E). Its `expanse show test` example prompts for a name, because `show` takes `-n`.
  - Source: task/adopt-docket inspection, 2026-10-11
  - Also: it credits the daemon with a global hotkey and custom keyboard shortcuts, which `expanse/daemon.py` does not have. Source: review/2026-10-12-1703-full.md, 2026-10-12
- [DOCS] `slim-claude-md` — **`CLAUDE.md` holds only Claude-specific guidance and defers to `AGENTS.md` and `ARCHITECTURE.md`.** It restates the architecture and development commands, some of them stale (`pip3 install -r pip-requirements.txt`, bare `pytest`).
  - Source: task/adopt-docket inspection, 2026-10-11
  - Also: it says to symlink `~/bin/expanse`, while on the user's machine that is a wrapper script around `~/.virtualenvs/expanse` (as `ARCHITECTURE.md` says). Source: review/2026-10-12-1703-full.md, 2026-10-12

## Needs proof of concept

### P0 Critical

### P1 High

### P2 Normal

### P3 Low

### Unprioritized

## Ready for separate work

### P0 Critical

### P1 High

### P2 Normal

### P3 Low

### Unprioritized
