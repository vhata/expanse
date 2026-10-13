# Architecture

What the structure is now, the boundaries parallel work must respect, and the invariants reviews check. Deferred work lives in [TODO.md](TODO.md); this file describes the code as it is.

## Layout

- `expanse/core.py`: the storage boundary. Locates `~/.expanserc` (`get_expfile`), loads, saves and validates it.
- `expanse/cli.py`: the Click CLI (`expanse`), subcommands `add`, `edit`, `delete`, `list`, `show`, `get`, `dump`. Entry point `expanse.cli:main`.
- `expanse/daemon.py`: optional rumps menu-bar app (`expanse-gui`, entry point `expanse.daemon:main`) that copies snippets to the clipboard with pyperclip. macOS only.
- `tests/`: pytest suite.
- `install.sh`, `com.expanse.daemon.plist`, `run.sh`: launchd and development helpers for the daemon. None of them works as written (`fix-daemon-install`, `fix-daemon-entry-points`).
- Outside the repository: `~/.hammerspoon/expanse.lua`, the preferred GUI, which shells out to the `expanse` CLI through `~/bin/expanse`. On the user's machine that is a wrapper script running a separate install in `~/.virtualenvs/expanse`, not any worktree's `.venv/`, so a change reaches Hammerspoon only once that install is updated.

## Shared interfaces

- The snippet file format, `{"expansions": {"<name>": "<content>"}}` at `$HOME/.expanserc`. The CLI and the daemon both read and write it through `expanse/core.py`. Every snippet's content is a string. `load_expansions` and `ensure_expfile` raise `StoreError` for a file that cannot be read or has any other shape, and a missing file loads as an empty store. `save_expansions` refuses to write any other shape and returns `False`, leaving the file as it was.
- The CLI surface used by the Hammerspoon integration: `expanse dump` prints each snippet as two lines, the name and then the content with newlines replaced by `↵`; and `expanse get -- <name>` prints the content followed by a newline, or prints nothing and exits 0 for an unknown name. Any command run against an unreadable or malformed store prints `Could not access expansion file <path>: <reason>` to stderr, prints nothing to stdout and exits non-zero. Changing either output or the exit status breaks `~/.hammerspoon/expanse.lua`, which is not in this repository; such a change needs the user to update that file in step.

## Invariants

- All file access to the snippet store goes through `expanse/core.py`.
- The location of the store comes from `$HOME`, so tests can point it at a temporary directory; tests never touch the real `~/.expanserc`.
- `expanse/core.py` and `expanse/cli.py` import nothing macOS-specific; only `expanse/daemon.py` imports rumps and pyperclip.

## Isolation for concurrent work

Each worktree owns its own `.venv/` (created by `bash scripts/setup.sh`) and ruff and pytest caches (`.ruff_cache/`, `.pytest_cache/`). All are ignored by git. Scripts resolve the virtualenv relative to the worktree they run in. Tests isolate the snippet store through `$HOME` or a mocked filesystem, so concurrent runs do not share state.

## Where to look first

`expanse/core.py`, then `expanse/cli.py`. Read `~/.hammerspoon/expanse.lua` before changing CLI output.
