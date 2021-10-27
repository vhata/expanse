import json
from io import StringIO
import pathlib
import os

from click.testing import CliRunner

from expanse import expanse

runner = CliRunner()

EMPTY_VALID_FILE = json.dumps({"expansions": {}})
VALID_FILE = json.dumps({"expansions": {"foo": "bar"}})
RC_FILENAME = pathlib.Path("/tmp/foo")


def test_ensure_expfile_valid(mocker):
    opener = mocker.mock_open(read_data=EMPTY_VALID_FILE)

    def mocked_open(self, *args, **kwargs):
        return opener(self, *args, **kwargs)

    mocker.patch("pathlib.Path.exists", return_value=True)
    mocker.patch.object(pathlib.Path, "open", mocked_open)
    assert expanse.ensure_expfile(RC_FILENAME) == True


def test_ensure_expfile_invalid(mocker):
    opener = mocker.mock_open(read_data="blegh")

    def mocked_open(self, *args, **kwargs):
        return opener(self, *args, **kwargs)

    mocker.patch("pathlib.Path.exists", return_value=True)
    mocker.patch.object(pathlib.Path, "open", mocked_open)
    assert expanse.ensure_expfile(RC_FILENAME) == False


def test_ensure_expfile_create(mocker, fs):
    opener = StringIO()

    mocker.patch("sys.stdin", StringIO("yes"))
    if not os.path.exists(RC_FILENAME.parent):
        fs.create_dir(RC_FILENAME.parent)
    # pyfakefs doesn't work well with pathlib
    mocker.patch("pathlib.Path.exists", return_value=False)
    mocker.patch("pathlib.PosixPath.exists", return_value=False)
    assert expanse.ensure_expfile(RC_FILENAME) == True
    assert RC_FILENAME.read_text() == EMPTY_VALID_FILE


def test_add(mocker, fs):
    mocker.patch("expanse.expanse.ensure_expfile", return_value=True)
    if not os.path.exists(RC_FILENAME.parent):
        fs.create_dir(RC_FILENAME.parent)
    fs.create_file(RC_FILENAME, contents=EMPTY_VALID_FILE)
    response = runner.invoke(
        expanse.cli,
        ["-f", str(RC_FILENAME), "add", "-n", "foo", "-e", "bar"],
    )
    assert response.exit_code == 0
    assert json.load(open(RC_FILENAME)) == json.loads(VALID_FILE)


def test_delete(mocker, fs):
    mocker.patch("expanse.expanse.ensure_expfile", return_value=True)
    if not os.path.exists(RC_FILENAME.parent):
        fs.create_dir(RC_FILENAME.parent)
    fs.create_file(RC_FILENAME, contents=VALID_FILE)
    response = runner.invoke(
        expanse.cli,
        ["-f", str(RC_FILENAME), "delete", "-n", "foo", "--yes"],
    )
    assert response.exit_code == 0
    assert json.load(open(RC_FILENAME)) == json.loads(EMPTY_VALID_FILE)
