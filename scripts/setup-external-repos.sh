#!/usr/bin/env bash
set -euo pipefail

mkdir -p external/reference

clone_or_skip () {
  local repo_url="$1"
  local target_dir="$2"

  if [ -d "$target_dir/.git" ]; then
    echo "Already exists: $target_dir"
  else
    echo "Cloning $repo_url into $target_dir"
    git clone "$repo_url" "$target_dir"
  fi
}

clone_or_skip https://github.com/EngramMemory/engram-memory.git external/reference/engram-memory
clone_or_skip https://github.com/microsoft/markitdown.git external/reference/markitdown
clone_or_skip https://github.com/Unstructured-IO/unstructured.git external/reference/unstructured
clone_or_skip https://github.com/microsoft/graphrag.git external/reference/graphrag
clone_or_skip https://github.com/getzep/graphiti.git external/reference/graphiti
clone_or_skip https://github.com/topoteretes/cognee.git external/reference/cognee
clone_or_skip https://github.com/kuzudb/kuzu.git external/reference/kuzu

echo "External reference repositories are ready."
echo "Next: open Claude Code from the project root and run /review-oss-all"
