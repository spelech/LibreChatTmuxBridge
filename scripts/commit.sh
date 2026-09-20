#!/usr/bin/env bash
set -e

# Change to repository root
cd "$(dirname "$0")/.."

if [ -z "$1" ]; then
    echo "Usage: ./commit.sh \"<commit_message>\""
    exit 1
fi

echo "🔍 Running Stage 1: Release & Link Integrity Verification..."
./scripts/verify_release.py

echo "🔍 Running Stage 2A: Python Lint & Tests..."
uv run ruff check src tests
uv run pytest

echo "🔍 Running Stage 2B: VitePress Documentation Build..."
npm run docs:build

echo "💾 Creating atomic commit: '$1'..."
git add -A
git commit -m "$1"
echo "✅ Atomic commit created successfully."
