#!/usr/bin/env bash
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

if [[ "${PREFIX:-}" == *com.termux* ]] || [[ -d /data/data/com.termux ]]; then
    exec python "Ghost Project.py"
fi

if [[ -x "$ROOT/.venv/bin/python" ]]; then
    exec "$ROOT/.venv/bin/python" "Ghost Project.py"
fi

if command -v python3 >/dev/null 2>&1; then
    exec python3 "Ghost Project.py"
fi

printf '%s\n' "Python is not installed. Run: bash Setup.sh"
exit 1
