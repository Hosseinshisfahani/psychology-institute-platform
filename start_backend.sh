#!/bin/zsh

set -eu

PROJECT_ROOT="/Users/hossein.sh.isfahani/projects/Emamy project"
BACKEND_VENV="$PROJECT_ROOT/pedendencies/venv/bin/activate"

if [ ! -f "$BACKEND_VENV" ]; then
  echo "Virtual environment not found at $BACKEND_VENV" >&2
  echo "Create it with: python -m venv \"$PROJECT_ROOT/pedendencies/venv\"" >&2
  exit 1
fi

cd "$PROJECT_ROOT"

# shellcheck disable=SC1090
source "$BACKEND_VENV"
exec python pedendencies/manage.py runserver

