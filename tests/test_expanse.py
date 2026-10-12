import json
import pathlib

import pytest
from click.testing import CliRunner

from expanse import cli, core

runner = CliRunner()

EMPTY_VALID_FILE = json.dumps({"expansions": {}})
VALID_FILE = json.dumps({"expansions": {"foo": "bar"}})


@pytest.fixture
def expfile(fs, monkeypatch):
    """The snippet store under a fake $HOME, so tests never touch ~/.expanserc."""
    home = pathlib.Path("/home/tester")
    fs.create_dir(home)
    monkeypatch.setenv("HOME", str(home))
    return home / ".expanserc"


def test_get_expfile_uses_home(expfile):
    assert core.get_expfile() == expfile


def test_ensure_expfile_valid(fs, expfile):
    fs.create_file(expfile, contents=EMPTY_VALID_FILE)
    assert core.ensure_expfile(expfile) is True


def test_ensure_expfile_invalid(fs, expfile):
    fs.create_file(expfile, contents="blegh")
    assert core.ensure_expfile(expfile) is False


def test_ensure_expfile_create(expfile):
    assert core.ensure_expfile(expfile) is True
    assert expfile.read_text() == EMPTY_VALID_FILE


def test_add(fs, expfile):
    fs.create_file(expfile, contents=EMPTY_VALID_FILE)
    response = runner.invoke(cli.cli, ["add", "-n", "foo", "-e", "bar"])
    assert response.exit_code == 0
    assert json.loads(expfile.read_text()) == json.loads(VALID_FILE)


def test_delete(fs, expfile):
    fs.create_file(expfile, contents=VALID_FILE)
    response = runner.invoke(cli.cli, ["delete", "-n", "foo", "--yes"])
    assert response.exit_code == 0
    assert json.loads(expfile.read_text()) == json.loads(EMPTY_VALID_FILE)
