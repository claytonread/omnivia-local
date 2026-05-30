"""
Local vault ingestion service.

Scans a local workspace or vault path and produces a structured inventory
of supported files. Source files are not modified.
"""

import os
import hashlib
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import List


# File types OmniVia can parse at ingest time.
SUPPORTED_EXTENSIONS = {".md", ".txt", ".markdown"}

# Directories and file patterns to skip during scanning.
SKIP_NAMES = {
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    ".git", ".svn", ".hg",
    "node_modules", ".venv", "venv", ".env",
    ".obsidian", ".trash", ".cache",
    ".DS_Store", "Thumbs.db",
    "dist", "build", "out", ".next", ".turbo", "coverage",
    ".parcel-cache", ".nuxt",
}

SKIP_PATTERNS = {".pyc", ".pyo", ".so", ".dylib", ".dll", ".exe"}
SKIP_PREFIXES = {"."}


@dataclass
class FileInventoryItem:
    """One file entry in the scan inventory."""
    path: str            # Relative path from workspace root
    extension: str       # e.g. ".md" or "" for no extension
    size: int            # File size in bytes
    modified_ms: int     # Modified time in milliseconds since epoch
    file_type: str       # e.g. "markdown", "text", "unsupported"
    parse_status: str    # "supported", "unsupported", "error", "skipped_dir"


@dataclass
class ScanResult:
    """Result of scanning a workspace path."""
    workspace_path: str
    total_files: int
    supported_files: int
    unsupported_files: int
    errors: int
    scan_duration_ms: int
    items: List[FileInventoryItem] = field(default_factory=list)


def _is_supported(path: Path) -> bool:
    """Check if a file has a supported extension."""
    return path.suffix.lower() in SUPPORTED_EXTENSIONS


def _should_skip(path: Path) -> bool:
    """Check if a path should be skipped (hidden, cache, generated, etc.)."""
    name = path.name

    # Skip hidden files/dirs unless they're approved exceptions
    if name.startswith("."):
        return name not in {".env.example", ".gitignore"}

    # Skip by exact name
    if name in SKIP_NAMES:
        return True

    # Skip by extension pattern
    for ext in SKIP_PATTERNS:
        if name.endswith(ext):
            return True

    return False


def _file_type_from_extension(ext: str) -> str:
    """Map file extension to a readable type label."""
    mapping = {
        ".md": "markdown",
        ".markdown": "markdown",
        ".txt": "text",
    }
    return mapping.get(ext.lower(), "unsupported")


def scan_workspace(
    workspace_path: str,
    max_files: int = 10000,
    follow_symlinks: bool = False,
) -> ScanResult:
    """Scan a local workspace and produce a file inventory.

    Args:
        workspace_path: Root path to scan.
        max_files: Safety cap to prevent runaway scans.
        follow_symlinks: If True, follow symbolic links (default False for safety).

    Returns:
        ScanResult with inventory items and statistics.
    """
    start = datetime.now()
    root = Path(workspace_path).resolve()

    if not root.is_dir():
        raise ValueError(f"Not a directory: {workspace_path}")

    items: List[FileInventoryItem] = []
    supported_count = 0
    unsupported_count = 0
    error_count = 0

    # Walk the directory tree manually for explicit control
    for dirpath, dirnames, filenames in os.walk(root, followlinks=follow_symlinks):
        dirpath = Path(dirpath)

        # Prune directories that should be skipped in-place
        dirnames[:] = [
            d for d in dirnames
            if not _should_skip(dirpath / d)
        ]

        for filename in filenames:
            file_path = dirpath / filename

            # Skip hidden files and cache/generated files
            if _should_skip(file_path):
                parse_status = "skipped_dir"
                file_type = "skipped"
            else:
                try:
                    stat = file_path.stat()
                    ext = file_path.suffix.lower()
                    file_type = _file_type_from_extension(ext)
                    is_supported = file_type in {"markdown", "text"}

                    parse_status = "supported" if is_supported else "unsupported"

                    if is_supported:
                        supported_count += 1
                    else:
                        unsupported_count += 1

                    items.append(FileInventoryItem(
                        path=str(file_path.relative_to(root)),
                        extension=ext,
                        size=stat.st_size,
                        modified_ms=int(stat.st_mtime * 1000),
                        file_type=file_type,
                        parse_status=parse_status,
                    ))
                except OSError as e:
                    error_count += 1
                    items.append(FileInventoryItem(
                        path=str(file_path.relative_to(root)),
                        extension=file_path.suffix.lower(),
                        size=0,
                        modified_ms=0,
                        file_type="error",
                        parse_status=f"error: {e}",
                    ))

            # Safety cap
            if len(items) >= max_files:
                break

        if len(items) >= max_files:
            break

    elapsed_ms = int((datetime.now() - start).total_seconds() * 1000)

    return ScanResult(
        workspace_path=workspace_path,
        total_files=len(items),
        supported_files=supported_count,
        unsupported_files=unsupported_count,
        errors=error_count,
        scan_duration_ms=elapsed_ms,
        items=items,
    )


def hash_file(path: Path, chunk_size: int = 65536) -> str:
    """Compute SHA-256 hash of a file's content."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def read_file_content(path: Path, max_chars: int = 500000) -> str:
    """Read text file content, limited to prevent memory issues.

    Returns the raw text. Caller decides how to chunk it for memory storage.
    """
    try:
        # Try UTF-8 first
        with open(path, "r", encoding="utf-8") as f:
            return f.read(max_chars)
    except UnicodeDecodeError:
        # Fall back to Latin-1 which maps all byte values 0-255
        with open(path, "r", encoding="latin-1") as f:
            return f.read(max_chars)
