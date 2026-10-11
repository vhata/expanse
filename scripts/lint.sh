#!/usr/bin/env bash
# Linter; any finding fails. Extra arguments are passed to ruff.
set -euo pipefail
source "$(dirname "$0")/_venv.sh"
cd "$ROOT"
exec "$VENV/bin/ruff" check "$@" .
