#!/usr/bin/env bash
# Formatter in write mode. Extra arguments are passed to ruff.
set -euo pipefail
source "$(dirname "$0")/_venv.sh"
cd "$ROOT"
exec "$VENV/bin/ruff" format "$@" .
