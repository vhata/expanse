"""Validation of the snippet store: malformed or unreadable stores are reported, never overwritten."""

import json
import os
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
    # An uncaught exception would leave something other than SystemExit here.
    assert result.exit_code == 1
    assert isinstance(result.exception, SystemExit)
    assert result.stdout == ""
    assert f"Could not access expansion file {expfile}: " in result.stderr


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
        {"expansions": {1: "a"}},
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
    "contents",
    [b'{"expansions": {"keep": "me"}}', MALFORMED["null value"]],
    ids=["valid", "malformed"],
)
def test_ensure_keeps_store_created_after_its_read(fs, expfile, monkeypatch, contents):
    """A store written by another process between the read and the create survives."""
    read = core._read_expansions
    calls = []

    def read_then_race(path):
        result = read(path)
        if not calls:
            fs.create_file(path, contents=contents)
        calls.append(path)
        return result

    monkeypatch.setattr(core, "_read_expansions", read_then_race)
    if contents == MALFORMED["null value"]:
        with pytest.raises(core.StoreError):
            core.ensure_expfile(expfile)
    else:
        core.ensure_expfile(expfile)
    assert expfile.read_bytes() == contents


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


def test_cli_malformed_store_reported_and_unchanged(fs, expfile, malformed):
    result = runner.invoke(cli.cli, COMMANDS["add"])
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


def test_cli_reports_malformed_store_before_prompting(fs, expfile):
    """The group checks the store before a command prompts for anything."""
    original = b'{"expansions": {"keep": "me", "n": null}}'
    fs.create_file(expfile, contents=original)
    result = runner.invoke(cli.cli, ["delete", "-n", "keep"], input="y\n")
    assert_reported(result)
    assert contents(fs, expfile) == original


def test_cli_creates_missing_store(fs, expfile):
    result = runner.invoke(cli.cli, ["dump"])
    assert result.exit_code == 0
    assert result.stdout == ""
    assert json.loads(contents(fs, expfile)) == {"expansions": {}}


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
    assert "Editor closed without saving; keep unchanged." in result.stderr
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


# Atomic save

SNIPPETS = {"expansions": {"keep": "me"}}
SNIPPETS_JSON = json.dumps(SNIPPETS)


def test_save_replaces_store_and_leaves_no_temp_file(fs, expfile):
    fs.create_file(expfile, contents='{"expansions": {}}')
    assert core.save_expansions(expfile, SNIPPETS) is True
    assert json.loads(expfile.read_text()) == SNIPPETS
    assert os.listdir(expfile.parent) == [expfile.name]


def test_save_interrupted_write_keeps_store(fs, expfile, monkeypatch):
    fs.create_file(expfile, contents=SNIPPETS_JSON)

    def partial_dump(obj, fp):
        fp.write('{"expansions": {"ke')
        raise OSError("disk full")

    monkeypatch.setattr(core.json, "dump", partial_dump)
    assert core.save_expansions(expfile, {"expansions": {}}) is False
    assert expfile.read_text() == SNIPPETS_JSON
    assert os.listdir(expfile.parent) == [expfile.name]


def test_replace_failure_other_than_oserror_keeps_store(fs, expfile):
    """Cleanup runs for any exception, not only OSError."""
    fs.create_file(expfile, contents=SNIPPETS_JSON)
    with pytest.raises(TypeError):
        core._replace_with_json(expfile, {"expansions": {"z": object()}})
    assert expfile.read_text() == SNIPPETS_JSON
    assert os.listdir(expfile.parent) == [expfile.name]


def test_save_preserves_mode(fs, expfile):
    fs.create_file(expfile, contents=SNIPPETS_JSON)
    os.chmod(expfile, 0o640)
    assert core.save_expansions(expfile, {"expansions": {}}) is True
    assert stat.S_IMODE(os.stat(expfile).st_mode) == 0o640


def test_save_refuses_write_protected_store(fs, expfile):
    fs.create_file(expfile, contents=SNIPPETS_JSON)
    os.chmod(expfile, 0o444)
    assert core.save_expansions(expfile, {"expansions": {}}) is False
    assert contents(fs, expfile) == SNIPPETS_JSON.encode()
    assert os.listdir(expfile.parent) == [expfile.name]


def test_new_store_mode_follows_umask(tmp_path, monkeypatch):
    # A real temporary $HOME: pyfakefs's os.open ignores the umask.
    monkeypatch.setenv("HOME", str(tmp_path))
    expfile = core.get_expfile()
    old_umask = os.umask(0o027)
    try:
        assert core.save_expansions(expfile, SNIPPETS) is True
    finally:
        os.umask(old_umask)
    assert stat.S_IMODE(os.stat(expfile).st_mode) == 0o640


def test_save_through_symlink_replaces_target(fs, expfile):
    target = expfile.parent / "dotfiles" / "expanserc"
    fs.create_file(target, contents='{"expansions": {}}')
    os.symlink(target, expfile)
    assert core.save_expansions(expfile, SNIPPETS) is True
    assert expfile.is_symlink()
    assert os.readlink(expfile) == str(target)
    assert json.loads(target.read_text()) == SNIPPETS
    assert os.listdir(target.parent) == [target.name]


def test_save_symlink_loop_fails(fs, expfile):
    os.symlink(expfile, expfile)
    assert core.save_expansions(expfile, {"expansions": {}}) is False
    assert expfile.is_symlink()
    assert os.listdir(expfile.parent) == [expfile.name]
