#!/usr/bin/env python3

import contextlib
import json
import os
import secrets
import stat
from pathlib import Path


class StoreError(Exception):
    """The snippet store could not be read, or is not a valid store."""


def get_expfile() -> Path:
    """Get the path to the expansions file."""
    return Path(os.environ.get("HOME", "/")) / Path(".expanserc")


def validate_expansions(store: object) -> None:
    """Raise StoreError unless store is a dict whose "expansions" maps str to str."""
    if not isinstance(store, dict):
        raise StoreError("the file is not a JSON object")
    expansions = store.get("expansions")
    if not isinstance(expansions, dict):
        raise StoreError('"expansions" is missing or is not a JSON object')
    for name, content in expansions.items():
        if not isinstance(name, str):
            raise StoreError(f"the name {name!r} is not a string")
        if not isinstance(content, str):
            raise StoreError(f"the content of {name!r} is not a string")


def _read_expansions(expfile: Path) -> dict | None:
    """Read and validate the expansions file, raising StoreError.

    Returns None if the file does not exist.
    """
    try:
        with expfile.open(encoding="utf-8") as f:
            store = json.load(f)
    except FileNotFoundError:
        return None
    except OSError as e:
        raise StoreError(e.strerror or str(e)) from e
    except json.JSONDecodeError as e:
        raise StoreError(f"invalid JSON: {e}") from e
    except ValueError as e:
        # UnicodeDecodeError, for a file that is not UTF-8.
        raise StoreError(str(e)) from e
    validate_expansions(store)
    return store


def load_expansions(expfile: Path) -> dict:
    """Load expansions from file; a missing file is an empty store.

    Raises StoreError if the file exists but cannot be read or is not a
    valid store, so a caller never mistakes a malformed store for an
    empty one and saves over it.
    """
    store = _read_expansions(expfile)
    return {"expansions": {}} if store is None else store


def _create_temp_beside(target: Path) -> tuple[int, str]:
    """Create and open a new, uniquely named file next to target.

    The file is created with mode 0o666, so the process umask applies to
    it as it would to a plain open().
    """
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_CLOEXEC
    for _ in range(100):
        tmp = os.path.join(target.parent, f".{target.name}.{secrets.token_hex(4)}.tmp")
        try:
            return os.open(tmp, flags, 0o666), tmp
        except FileExistsError:
            continue
    raise FileExistsError(f"no free temporary file name beside {target}")


def _replace_with_json(expfile: Path, data: dict) -> None:
    """Atomically replace expfile with data serialised as JSON.

    The JSON is written to a temporary file in the same directory, flushed
    and renamed over the store, so an interrupted write leaves the previous
    contents in place. A symlinked store has its target replaced and the
    link kept. An existing store keeps its permission bits; a new one gets
    the mode the process umask gives it.
    """
    target = Path(os.path.realpath(expfile))
    try:
        mode = stat.S_IMODE(target.stat().st_mode)
    except FileNotFoundError:
        mode = None

    fd, tmp = _create_temp_beside(target)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            if mode is not None:
                os.fchmod(f.fileno(), mode)
            json.dump(data, f)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, target)
    except BaseException:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(tmp)
        raise


def save_expansions(expfile: Path, expansions: dict) -> bool:
    """Save expansions to file, replacing it atomically.

    Returns False, leaving the file untouched, if expansions is not a
    valid store or the file cannot be written.
    """
    try:
        validate_expansions(expansions)
    except StoreError:
        return False
    try:
        _replace_with_json(expfile, expansions)
        return True
    except OSError:
        return False


def ensure_expfile(expfile: Path) -> None:
    """Ensure the expansions file exists and is valid, raising StoreError."""
    if _read_expansions(expfile) is not None:
        return
    try:
        # "x" never truncates a file created since the read above.
        with expfile.open("x") as f:
            json.dump({"expansions": {}}, f)
    except FileExistsError:
        _read_expansions(expfile)
    except OSError as e:
        raise StoreError(e.strerror or str(e)) from e
