#!/usr/bin/env bash
# Auto-format all frontend files using Prettier.
set -e

FRONTEND_DIR="$(cd "$(dirname "$0")/../frontend" && pwd)"

cd "$FRONTEND_DIR"

if [ ! -d node_modules ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

echo "Formatting frontend files..."
npx prettier --write .
echo "Done."
