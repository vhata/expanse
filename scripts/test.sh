#!/usr/bin/env bash
# Unit tests. pytest exits 5 when nothing is collected, which fails this gate.
# Extra arguments are passed to pytest.
set -euo pipefail
source "$(dirname "$0")/_venv.sh"
cd "$ROOT"
exec "$VENV/bin/python" -m pytest --strict-markers "$@"
