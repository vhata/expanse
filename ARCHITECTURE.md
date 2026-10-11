# Architecture

What the structure is now, the boundaries parallel work must respect, and the invariants reviews check. Deferred work lives in [TODO.md](TODO.md); this file describes the code as it is.

## Layout

- `expanse/core.py`: the storage boundary. Locates `~/.expanserc` (`get_expfile`), loads, saves and validates it.
- `expanse/cli.py`: the Click CLI (`expanse`), subcommands `add`, `edit`, `delete`, `list`, `show`, `get`, `dump`. Entry point `expanse.cli:main`.
- `expanse/daemon.py`: optional rumps menu-bar app (`expanse-gui`, entry point `expanse.daemon:main`) that copies snippets to the clipboard with pyperclip. macOS only.
- `tests/`: pytest suite.
- `install.sh`, `com.expanse.daemon.plist`, `run.sh`: launchd and development helpers for the daemon.
- Outside the repository: `~/.hammerspoon/expanse.lua`, the preferred GUI, which shells out to the `expanse` CLI through a `~/bin/expanse` symlink.

## Shared interfaces

- The snippet file format, `{"expansions": {"<name>": "<content>"}}` at `$HOME/.expanserc`. The CLI and the daemon both read and write it through `expanse/core.py`.
- The CLI surface used by the Hammerspoon integration: `expanse dump` prints each snippet as two lines, the name and then the content with newlines replaced by `↵`; and `expanse get -- <name>` prints the content followed by a newline, or prints nothing and exits 0 for an unknown name. Changing either output or the exit status breaks `~/.hammerspoon/expanse.lua`, which is not in this repository; such a change needs the user to update that file in step.

## Invariants

- All file access to the snippet store goes through `expanse/core.py`.
- The location of the store comes from `$HOME`, so tests can point it at a temporary directory; tests never touch the real `~/.expanserc`.
- `expanse/core.py` and `expanse/cli.py` import nothing macOS-specific; only `expanse/daemon.py` imports rumps and pyperclip.

## Isolation for concurrent work

Each worktree owns its own `.venv/` (created by `bash scripts/setup.sh`) and ruff and pytest caches (`.ruff_cache/`, `.pytest_cache/`). All are ignored by git. Scripts resolve the virtualenv relative to the worktree they run in. Tests isolate the snippet store through `$HOME` or a mocked filesystem, so concurrent runs do not share state.

## Where to look first

`expanse/core.py`, then `expanse/cli.py`. Read `~/.hammerspoon/expanse.lua` before changing CLI output.
