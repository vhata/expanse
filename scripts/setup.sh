#!/usr/bin/env bash
# Prepare this worktree: create its own virtualenv from Python 3.12, install
# the package in editable mode plus the pinned development tools, and point
# git at the tracked hooks. Idempotent; run after cloning, creating a
# worktree, or changing hook configuration.
set -euo pipefail
cd "$(dirname "$0")/.."

PY="${PYTHON:-$(command -v python3.12 || command -v python3)}"
if ! "$PY" -c 'import sys; sys.exit(sys.version_info[:2] != (3, 12))'; then
  echo "setup: $PY is not Python 3.12 (see .python-version); set PYTHON=/path/to/python3.12" >&2
  exit 1
fi

[ -x .venv/bin/python ] || "$PY" -m venv .venv
.venv/bin/python -m pip install --quiet -e . -r requirements-dev.txt

git config core.hooksPath .githooks

echo "setup: done. Run 'bash scripts/check.sh' to verify the baseline."
