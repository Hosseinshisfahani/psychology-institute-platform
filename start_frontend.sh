#!/bin/zsh

set -eu

FRONTEND_DIR="/Users/hossein.sh.isfahani/projects/Emamy project/frontend"

if [ ! -d "$FRONTEND_DIR" ]; then
  echo "Frontend directory not found at $FRONTEND_DIR" >&2
  exit 1
fi

cd "$FRONTEND_DIR"

if [ ! -d "node_modules" ]; then
  echo "node_modules not found. Installing dependencies..." >&2
  npm install
fi

exec npm start

