#!/usr/bin/env python3

import json
import os
from pathlib import Path


def get_expfile() -> Path:
    """Get the path to the expansions file."""
    return Path(os.environ.get("HOME", "/")) / Path(".expanserc")


def load_expansions(expfile: Path) -> dict:
    """Load expansions from file."""
    if not expfile.exists():
        return {"expansions": {}}
    try:
        with expfile.open() as f:
            return json.load(f)
    except (json.JSONDecodeError, KeyError):
        return {"expansions": {}}


def save_expansions(expfile: Path, expansions: dict) -> bool:
    """Save expansions to file."""
    try:
        with expfile.open("w") as f:
            json.dump(expansions, f)
        return True
    except OSError:
        return False


def ensure_expfile(expfile: Path) -> bool:
    """Ensure the expansions file exists and is valid."""
    if expfile.exists():
        try:
            with expfile.open() as f:
                json.load(f)["expansions"]
        except (json.JSONDecodeError, KeyError):
            return False
        return True

    try:
        with expfile.open("w") as f:
            json.dump({"expansions": {}}, f)
        return True
    except OSError:
        return False
