#!/usr/bin/env bash
set -euo pipefail

mkdir -p external/reference
mkdir -p external/sidecars
mkdir -p external/vendor
mkdir -p docs/open-source
mkdir -p docs/adr
mkdir -p .claude/commands

touch external/reference/.gitkeep
touch external/sidecars/.gitkeep
touch external/vendor/.gitkeep

echo "Created external folders and documentation folders."
