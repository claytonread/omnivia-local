#!/usr/bin/env bash
set -euo pipefail

echo "OmniVia DoD Status"
echo ""

echo "Changed files:"
git status --short || true

echo ""
echo "Diff summary:"
git diff --stat || true

echo ""
echo "Recent quality reports:"
ls -lt docs/quality/reviews 2>/dev/null | head -10 || echo "No review reports found"

echo ""
echo "Potential external/reference imports:"
grep -R "external/reference" services apps packages 2>/dev/null || echo "No external/reference imports found"
