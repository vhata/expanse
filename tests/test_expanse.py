import json

import pytest
from click.testing import CliRunner

from expanse import cli, core

runner = CliRunner()

EMPTY_VALID_FILE = json.dumps({"expansions": {}})
VALID_FILE = json.dumps({"expansions": {"foo": "bar"}})


def test_get_expfile_uses_home(expfile):
    assert core.get_expfile() == expfile


def test_ensure_expfile_valid(fs, expfile):
    fs.create_file(expfile, contents=EMPTY_VALID_FILE)
    core.ensure_expfile(expfile)
    assert expfile.read_text() == EMPTY_VALID_FILE


def test_ensure_expfile_invalid(fs, expfile):
    fs.create_file(expfile, contents="blegh")
    with pytest.raises(core.StoreError):
        core.ensure_expfile(expfile)
    assert expfile.read_text() == "blegh"


def test_ensure_expfile_create(expfile):
    core.ensure_expfile(expfile)
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


# The `dump` and `get` output below is the interface ~/.hammerspoon/expanse.lua
# parses (ARCHITECTURE.md, "Shared interfaces"), so these tests pin it exactly.

CONTRACT_FILE = json.dumps(
    {
        "expansions": {
            "foo": "bar",
            "multi": "line one\nline two\n",
            "-dash": "starts with a dash",
            "empty": "",
        }
    }
)


def test_dump(fs, expfile):
    fs.create_file(expfile, contents=CONTRACT_FILE)
    response = runner.invoke(cli.cli, ["dump"])
    assert response.exit_code == 0
    # one name line and one content line per snippet, in store order
    assert response.stdout == "".join(
        [
            "foo\nbar\n",
            "multi\nline one↵line two↵\n",
            "-dash\nstarts with a dash\n",
            "empty\n\n",
        ]
    )
    assert response.stderr == ""


def test_dump_empty_store(fs, expfile):
    fs.create_file(expfile, contents=EMPTY_VALID_FILE)
    response = runner.invoke(cli.cli, ["dump"])
    assert response.exit_code == 0
    assert response.stdout == ""


@pytest.mark.parametrize(
    ("name", "stdout"),
    [
        pytest.param("foo", "bar\n", id="foo"),
        pytest.param("multi", "line one\nline two\n\n", id="multi"),
        pytest.param("-dash", "starts with a dash\n", id="dash"),
        pytest.param("empty", "\n", id="empty"),
        pytest.param("unknown", "", id="unknown"),
    ],
)
def test_get(fs, expfile, name, stdout):
    fs.create_file(expfile, contents=CONTRACT_FILE)
    response = runner.invoke(cli.cli, ["get", "--", name])
    assert response.exit_code == 0
    assert response.stdout == stdout
    assert response.stderr == ""


def test_get_several_names(fs, expfile):
    fs.create_file(expfile, contents=CONTRACT_FILE)
    response = runner.invoke(cli.cli, ["get", "--", "foo", "unknown", "-dash"])
    assert response.exit_code == 0
    assert response.stdout == "bar\nstarts with a dash\n"


def test_list(fs, expfile):
    fs.create_file(expfile, contents=CONTRACT_FILE)
    response = runner.invoke(cli.cli, ["list"])
    assert response.exit_code == 0
    assert response.stdout == "foo\nmulti\n-dash\nempty\n"


def test_show(fs, expfile):
    fs.create_file(expfile, contents=CONTRACT_FILE)
    response = runner.invoke(cli.cli, ["show", "-n", "multi"])
    assert response.exit_code == 0
    assert response.stdout == "'multi'\nline one\nline two\n\n"


def test_show_unknown(fs, expfile):
    fs.create_file(expfile, contents=CONTRACT_FILE)
    response = runner.invoke(cli.cli, ["show", "-n", "unknown"])
    assert response.exit_code == 1
    assert response.stdout == ""
    assert "No such expansion: unknown" in response.stderr


@pytest.fixture
def fake_editor(monkeypatch):
    """Replace click.edit: record the text it was given and return `result`.

    A test must set `result`; an unset result raises rather than return
    None, which is what click.edit returns on an aborted edit, so a test of
    that case sets `result = None` explicitly.
    """
    calls = []
    unset = object()

    def edit(text=None, **kwargs):
        calls.append(text)
        if edit.result is unset:
            raise AssertionError("fake_editor.result was not set")
        return edit.result

    edit.calls = calls
    edit.result = unset
    monkeypatch.setattr("click.edit", edit)
    return edit


def test_edit_existing(fs, expfile, fake_editor):
    fs.create_file(expfile, contents=CONTRACT_FILE)
    fake_editor.result = "edited\ncontent"
    response = runner.invoke(cli.cli, ["edit", "-n", "multi"])
    assert response.exit_code == 0
    assert response.stdout == ""
    assert fake_editor.calls == ["line one\nline two\n"]
    expansions = json.loads(expfile.read_text())["expansions"]
    assert expansions["multi"] == "edited\ncontent"
    assert expansions["foo"] == "bar"


def test_edit_new(fs, expfile, fake_editor):
    fs.create_file(expfile, contents=VALID_FILE)
    fake_editor.result = "fresh"
    response = runner.invoke(cli.cli, ["edit", "-n", "new"])
    assert response.exit_code == 0
    assert response.stdout == "No such expansion: new, creating new one\n"
    assert fake_editor.calls == [""]
    assert json.loads(expfile.read_text()) == {"expansions": {"foo": "bar", "new": "fresh"}}


def test_edit_abort_keeps_existing_snippet(fs, expfile, fake_editor):
    fs.create_file(expfile, contents=VALID_FILE)
    fake_editor.result = None  # the editor exited without saving
    response = runner.invoke(cli.cli, ["edit", "-n", "foo"])
    assert response.exit_code == 1
    assert isinstance(response.exception, SystemExit)  # clean exit, no traceback
    assert response.stderr == "Editor closed without saving; foo unchanged.\n"
    assert expfile.read_text() == VALID_FILE


def test_edit_abort_does_not_create_snippet(fs, expfile, fake_editor):
    fs.create_file(expfile, contents=VALID_FILE)
    fake_editor.result = None  # the editor exited without saving
    response = runner.invoke(cli.cli, ["edit", "-n", "new"])
    assert response.exit_code == 1
    assert isinstance(response.exception, SystemExit)  # clean exit, no traceback
    assert response.stderr == "Editor closed without saving; new not created.\n"
    assert expfile.read_text() == VALID_FILE
