#!/usr/bin/env bash
set -euo pipefail

echo "Changed files:"
git status --short

echo ""
echo "Diff summary:"
git diff --stat

echo ""
echo "Files changed since HEAD:"
git diff --name-only
