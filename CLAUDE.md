# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Expanse is a text snippet manager for macOS with multiple interfaces:
1. **CLI (`expanse`)** - Command-line interface for managing snippets
2. **Hammerspoon integration** - Preferred GUI via `~/.hammerspoon/expanse.lua` (Cmd+Alt+E)
3. **GUI daemon (`expanse-gui`)** - Alternative menu bar app (rumps-based, more complex)

Snippets are stored as JSON in `~/.expanserc`.

## Hammerspoon Integration

**Preferred approach**: The Hammerspoon integration (`~/.hammerspoon/expanse.lua`) provides a cleaner, more integrated experience:

- **Hotkey**: `Cmd+Alt+E` triggers snippet chooser
- **Interface**: Uses `hs.chooser` with search functionality  
- **Backend**: Calls `expanse` CLI commands via `hs.execute()`
- **Clipboard**: Automatically copies selected snippet
- **Display**: Truncates long snippets for better UX
- **Dependencies**: Requires `~/bin/expanse` symlink to CLI

This approach eliminates the need for the complex rumps daemon while providing superior integration with the existing Hammerspoon workflow.

## Development Commands

```bash
# Install in development mode
pip install -e .

# Install from pip-requirements.txt (alternative)
pip3 install -r pip-requirements.txt

# Run tests
pytest

# Setup Hammerspoon integration (preferred)
ln -sf $(which expanse) ~/bin/expanse

# Legacy daemon options (if not using Hammerspoon)
./run.sh  # Quick development daemon run (adds current dir to PYTHONPATH)
python3 -m expanse.daemon  # Manual daemon run
```

## Architecture

### Core Components

- **`expanse/core.py`** - File I/O operations for snippet storage
  - `get_expfile()` - Returns `~/.expanserc` path
  - `load_expansions()` / `save_expansions()` - JSON serialization
  - `ensure_expfile()` - File validation/creation

- **`expanse/cli.py`** - Click-based CLI with subcommands
  - Commands: `add`, `edit`, `delete`, `list`, `show`, `get`, `dump`
  - Uses Click's `@click.group()` pattern

- **`expanse/daemon.py`** - rumps-based GUI daemon (legacy)
  - `ExpanseDaemon` class extends `rumps.App`
  - Menu items for each snippet + management actions
  - Uses `pyperclip` for clipboard operations
  - **Note**: Hammerspoon integration is preferred over this daemon

### Entry Points

The `setup.py` defines two console scripts:
- `expanse` → `expanse.cli:main` (CLI)
- `expanse-gui` → `expanse.daemon:main` (GUI daemon)

### Data Format

Snippets are stored as JSON:
```json
{
  "expansions": {
    "snippet_name": "snippet_content"
  }
}
```

## Testing

Tests use:
- `pytest` with `click.testing.CliRunner`
- `pytest-mock` for mocking
- `pyfakefs` for filesystem simulation

Run individual tests: `pytest tests/test_expanse.py::test_function_name`