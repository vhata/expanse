"""Validation of the snippet store: malformed or unreadable stores are reported, never overwritten."""

import json
import stat

import pytest
from click.testing import CliRunner

from expanse import cli, core

runner = CliRunner()

MALFORMED = {
    "invalid JSON": b'{"expansions": {"keep": "me"},',
    "invalid UTF-8": b'{"expansions": {"a": "\xff"}}',
    "top level is a list": b"[]",
    "top level is a string": b'"expansions"',
    "top level is null": b"null",
    "no expansions key": b'{"other": {}}',
    "expansions is a list": b'{"expansions": []}',
    "expansions is null": b'{"expansions": null}',
    "integer value": b'{"expansions": {"a": 1}}',
    "null value": b'{"expansions": {"keep": "me", "n": null}}',
    "list value": b'{"expansions": {"a": ["b"]}}',
}

COMMANDS = {
    "add": ["add", "-n", "new", "-e", "content"],
    "edit": ["edit", "-n", "keep"],
    "delete": ["delete", "-n", "keep", "--yes"],
    "list": ["list"],
    "show": ["show", "-n", "keep"],
    "get": ["get", "--", "keep"],
    "dump": ["dump"],
}


@pytest.fixture(params=MALFORMED.values(), ids=MALFORMED.keys())
def malformed(request, fs, expfile):
    """A malformed store; returns its original bytes."""
    fs.create_file(expfile, contents=request.param)
    return request.param


@pytest.fixture(params=["directory", "unreadable"])
def inaccessible(request, fs, expfile):
    """A store path that exists but cannot be read as a file."""
    if request.param == "directory":
        fs.create_dir(expfile)
    else:
        fs.create_file(expfile, contents=b'{"expansions": {}}', st_mode=stat.S_IFREG)
    return request.param


@pytest.fixture(params=[True, False], ids=["file", "no file"])
def unsearchable_home(request, tmp_path, monkeypatch):
    """A temporary $HOME without search permission; returns its path.

    This uses the real filesystem, because pyfakefs reports a missing file
    in such a directory as FileNotFoundError where macOS raises
    PermissionError.
    """
    home = tmp_path / "home"
    home.mkdir()
    if request.param:
        (home / ".expanserc").write_text('{"expansions": {}}')
    monkeypatch.setenv("HOME", str(home))
    home.chmod(0o600)
    yield home
    home.chmod(0o700)


def contents(fs, path):
    """The file's bytes, read without going through its permissions."""
    return fs.get_object(path).byte_contents


def assert_reported(result, expfile="/home/tester/.expanserc"):
    assert result.exit_code != 0
    assert result.stdout == ""
    assert f"Could not access expansion file {expfile}: " in result.stderr
    assert "Traceback" not in result.output


# Core


def test_load_missing_is_empty_and_creates_nothing(expfile):
    assert core.load_expansions(expfile) == {"expansions": {}}
    assert not expfile.exists()


def test_load_valid_store(fs, expfile):
    store = {"expansions": {"a": "one", "b": "línea\ndos"}, "extra": 1}
    fs.create_file(expfile, contents=json.dumps(store, ensure_ascii=False).encode())
    assert core.load_expansions(expfile) == store


def test_save_valid_store(fs, expfile):
    fs.create_file(expfile, contents=b'{"expansions": {}}')
    assert core.save_expansions(expfile, {"expansions": {"a": "one"}}) is True
    assert json.loads(contents(fs, expfile)) == {"expansions": {"a": "one"}}


@pytest.mark.parametrize(
    "store",
    [
        {"expansions": {"keep": "me", "n": None}},
        {"expansions": {"a": 1}},
        {"expansions": []},
        [],
    ],
)
def test_save_refuses_invalid_store(fs, expfile, store):
    original = b'{"expansions": {"keep": "me"}}'
    fs.create_file(expfile, contents=original)
    assert core.save_expansions(expfile, store) is False
    assert contents(fs, expfile) == original


def test_save_invalid_store_creates_nothing(expfile):
    assert core.save_expansions(expfile, {"expansions": {"n": None}}) is False
    assert not expfile.exists()


def test_load_malformed_raises(fs, expfile, malformed):
    with pytest.raises(core.StoreError):
        core.load_expansions(expfile)
    assert contents(fs, expfile) == malformed


def test_ensure_malformed_raises(fs, expfile, malformed):
    with pytest.raises(core.StoreError):
        core.ensure_expfile(expfile)
    assert contents(fs, expfile) == malformed


def test_load_inaccessible_raises(expfile, inaccessible):
    with pytest.raises(core.StoreError):
        core.load_expansions(expfile)


def test_ensure_inaccessible_raises(expfile, inaccessible):
    with pytest.raises(core.StoreError):
        core.ensure_expfile(expfile)


def test_unsearchable_home_raises(unsearchable_home):
    expfile = core.get_expfile()
    with pytest.raises(core.StoreError, match="Permission denied"):
        core.load_expansions(expfile)
    with pytest.raises(core.StoreError, match="Permission denied"):
        core.ensure_expfile(expfile)


def test_ensure_uncreatable_raises(fs, expfile):
    fs.chmod(expfile.parent, 0o555)
    with pytest.raises(core.StoreError):
        core.ensure_expfile(expfile)
    assert not expfile.exists()


@pytest.mark.parametrize(
    "store, message",
    [
        (b'{"expansions": {"n": null}}', "'n' is not a string"),
        (b'{"expansions": []}', '"expansions" is missing or is not a JSON object'),
        (b"blegh", "invalid JSON: "),
        (b"\xff", "can't decode byte 0xff"),
    ],
)
def test_store_error_names_the_problem(fs, expfile, store, message):
    fs.create_file(expfile, contents=store)
    with pytest.raises(core.StoreError, match=message):
        core.load_expansions(expfile)


# CLI


@pytest.mark.parametrize("command", ["add", "get", "dump"])
def test_cli_malformed_store_reported_and_unchanged(fs, expfile, malformed, command):
    result = runner.invoke(cli.cli, COMMANDS[command])
    assert_reported(result)
    assert contents(fs, expfile) == malformed


@pytest.mark.parametrize("command", COMMANDS.keys())
def test_every_command_reports_malformed_store(fs, expfile, command):
    original = b'{"expansions": {"keep": "me", "n": null}}'
    fs.create_file(expfile, contents=original)
    result = runner.invoke(cli.cli, COMMANDS[command], env={"EDITOR": "false"})
    assert_reported(result)
    assert contents(fs, expfile) == original


@pytest.mark.parametrize("command", ["add", "dump"])
def test_cli_inaccessible_store_reported(expfile, inaccessible, command):
    result = runner.invoke(cli.cli, COMMANDS[command])
    assert_reported(result)


@pytest.mark.parametrize("command", ["add", "dump"])
def test_cli_unsearchable_home_reported(unsearchable_home, command):
    result = runner.invoke(cli.cli, COMMANDS[command])
    assert_reported(result, unsearchable_home / ".expanserc")


def test_cli_reports_store_error_from_a_command(fs, expfile, monkeypatch):
    """A command's own load is covered too, not only the group's ensure_expfile check."""
    original = b'{"expansions": []}'
    fs.create_file(expfile, contents=original)
    monkeypatch.setattr(cli, "ensure_expfile", lambda expfile: None)
    result = runner.invoke(cli.cli, COMMANDS["add"])
    assert_reported(result)
    assert contents(fs, expfile) == original


def test_cli_edit_aborted_in_editor_leaves_store_unchanged(fs, expfile, monkeypatch):
    """click.edit returns None when the editor exits without saving; that is never stored."""
    original = b'{"expansions": {"keep": "me"}}'
    fs.create_file(expfile, contents=original)
    monkeypatch.setattr(cli.click, "edit", lambda *args, **kwargs: None)
    result = runner.invoke(cli.cli, COMMANDS["edit"])
    assert result.exit_code != 0
    assert "Could not write to /home/tester/.expanserc." in result.stderr
    assert contents(fs, expfile) == original


def test_cli_store_behind_dangling_symlink(fs, expfile):
    """A dangling symlink loads as an empty store, and the first save creates its target."""
    target = expfile.parent / "dotfiles" / "expanserc"
    fs.create_dir(target.parent)
    fs.create_symlink(expfile, target)
    assert runner.invoke(cli.cli, ["dump"]).exit_code == 0
    result = runner.invoke(cli.cli, COMMANDS["add"])
    assert result.exit_code == 0
    assert json.loads(contents(fs, target)) == {"expansions": {"new": "content"}}
    assert expfile.is_symlink()
