#!/usr/bin/env bash
# Run all frontend quality checks (format + lint).
# Exits with non-zero status if any check fails.
set -e

FRONTEND_DIR="$(cd "$(dirname "$0")/../frontend" && pwd)"

cd "$FRONTEND_DIR"

if [ ! -d node_modules ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

FAILED=0

echo "--- Prettier (format check) ---"
if npx prettier --check .; then
    echo "PASS: formatting"
else
    echo "FAIL: run ./scripts/format-frontend.sh to fix"
    FAILED=1
fi

echo ""
echo "--- ESLint (lint) ---"
if npx eslint script.js; then
    echo "PASS: linting"
else
    echo "FAIL: run 'cd frontend && npm run lint:fix' to auto-fix"
    FAILED=1
fi

echo ""
if [ "$FAILED" -eq 0 ]; then
    echo "All frontend checks passed."
else
    echo "Some checks failed. See above."
    exit 1
fi
