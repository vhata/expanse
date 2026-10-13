# Expanse

A text snippet manager for macOS. Snippets are named pieces of text kept in a JSON file at `~/.expanserc`; the `expanse` command manages them, and a Hammerspoon hotkey picks one and copies it to the clipboard.

## Command line

```bash
# Add a snippet; without -e, the content is read from stdin until Ctrl-D
expanse add -n test -e "Some long text you want to expand to"

# Edit a snippet in $EDITOR (creates it if it does not exist)
expanse edit -n test

# Print a snippet's name and content
expanse show -n test

# Print the content of one or more snippets
expanse get test

# List snippet names
expanse list

# Print every snippet as two lines: the name, then the content with
# newlines shown as ↵
expanse dump

# Delete a snippet (asks for confirmation unless --yes is given)
expanse delete -n test
```

`add`, `edit`, `show` and `delete` prompt for the name when `-n` is left out. `add` asks before overwriting an existing snippet. `get` prints nothing for a name that does not exist; use `expanse get -- <name>` for a name that starts with `-`.

## Hammerspoon

Pressing Cmd+Alt+E opens a Hammerspoon chooser listing every snippet by name, with the start and end of its content underneath. Typing filters on both name and content, and choosing a snippet copies its content to the clipboard.

The Hammerspoon config is not part of this repository. It lives at `~/.hammerspoon/expanse.lua`, is loaded with `require("expanse")` from `~/.hammerspoon/init.lua`, and runs `~/bin/expanse dump` and `~/bin/expanse get`, so `~/bin/expanse` has to run the CLI. See [ARCHITECTURE.md](ARCHITECTURE.md) for how that is set up and which CLI output the config depends on.

## Menu-bar app

`expanse-gui` starts an optional menu-bar app (using rumps) that lists the snippets and copies one to the clipboard when clicked, with menu items to add, edit and delete snippets. It needs `rumps` and `pyperclip` installed in the same environment.

## Development

```bash
bash scripts/setup.sh   # creates .venv/ from Python 3.12 and installs the package editable
bash scripts/check.sh   # format check, lint and tests
```

The gates, test policy and CI are described in [docs/QUALITY.md](docs/QUALITY.md), and the code layout and invariants in [ARCHITECTURE.md](ARCHITECTURE.md). Work is tracked in [TODO.md](TODO.md); see [AGENTS.md](AGENTS.md) for the workflow.

Expanse is developed with help from Claude Code.
