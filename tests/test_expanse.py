import json
from io import StringIO
from pathlib import Path

from click.testing import CliRunner

from expanse import expanse

runner = CliRunner()

EMPTY_VALID_FILE = json.dumps({"expansions": {}})
RC_FILENAME = Path("/foo")


def test_ensure_expfile_valid(mocker):
    opener = mocker.mock_open(read_data=EMPTY_VALID_FILE)

    def mocked_open(self, *args, **kwargs):
        return opener(self, *args, **kwargs)

    mocker.patch("pathlib.Path.exists", return_value=True)
    mocker.patch.object(Path, "open", mocked_open)
    assert expanse.ensure_expfile(RC_FILENAME) == True


def test_ensure_expfile_invalid(mocker):
    opener = mocker.mock_open(read_data="blegh")

    def mocked_open(self, *args, **kwargs):
        return opener(self, *args, **kwargs)

    mocker.patch("pathlib.Path.exists", return_value=True)
    mocker.patch.object(Path, "open", mocked_open)
    assert expanse.ensure_expfile(RC_FILENAME) == False


def test_ensure_expfile_create(mocker, fs):
    opener = StringIO()

    mocker.patch("sys.stdin", StringIO("yes"))
    assert expanse.ensure_expfile(RC_FILENAME) == True
    assert RC_FILENAME.read_text() == EMPTY_VALID_FILE
