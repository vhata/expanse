# Sourced by the gate scripts: resolve this worktree's virtualenv.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$ROOT/.venv"
if [ ! -x "$VENV/bin/python" ]; then
  echo "$(basename "$0"): $VENV missing; run 'bash scripts/setup.sh'" >&2
  exit 1
fi
