import pathlib

import pytest


@pytest.fixture
def expfile(fs, monkeypatch):
    """The snippet store under a fake $HOME, so tests never touch ~/.expanserc."""
    home = pathlib.Path("/home/tester")
    fs.create_dir(home)
    monkeypatch.setenv("HOME", str(home))
    return home / ".expanserc"
