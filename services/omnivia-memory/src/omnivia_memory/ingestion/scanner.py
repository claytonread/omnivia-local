"""File scanner for discovering source files."""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from omnivia_memory.ingestion.models import FileType


DEFAULT_IGNORE_PATTERNS = [
    ".git",
    ".svn",
    ".hg",
    "__pycache__",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "*.egg-info",
    ".eggs",
    "node_modules",
    "bower_components",
    ".npm",
    ".yarn",
    "build",
    "dist",
    "target",
    ".gradle",
    ".next",
    ".nuxt",
    ".output",
    ".venv",
    "venv",
    "env",
    ".env",
    ".vscode",
    ".idea",
    "*.swp",
    "*.swo",
    "*~",
    ".DS_Store",
    "Thumbs.db",
    ".pip",
    ".cargo",
    "vendor",
]


@dataclass
class ScanOptions:
    """Options for file scanning."""

    root_path: Path
    ignore_patterns: list[str] = field(default_factory=list)
    max_depth: int | None = None
    follow_symlinks: bool = False


@dataclass
class FileInfo:
    """Information about a discovered file."""

    path: Path
    file_type: FileType
    size: int
    modified_time: str | None = None

    def __str__(self) -> str:
        return f"FileInfo({self.path}, type={self.file_type.value})"


class FileScanner:
    """Scans directories for source files."""

    EXTENSION_MAP = {
        ".md": FileType.MARKDOWN,
        ".markdown": FileType.MARKDOWN,
        ".pdf": FileType.PDF,
        ".docx": FileType.DOCX,
    }

    def scan(self, options: ScanOptions) -> list[FileInfo]:
        """Scan directory for source files."""
        if not options.root_path.exists() or not options.root_path.is_dir():
            return []

        ignore_patterns = list(DEFAULT_IGNORE_PATTERNS) + options.ignore_patterns
        results: list[FileInfo] = []
        self._scan_recursive(
            options.root_path,
            options.max_depth,
            options.follow_symlinks,
            ignore_patterns,
            results,
        )
        return results

    def _scan_recursive(
        self,
        current_path: Path,
        max_depth: int | None,
        follow_symlinks: bool,
        ignore_patterns: list[str],
        results: list[FileInfo],
        current_depth: int = 0,
    ) -> None:
        if max_depth is not None and current_depth > max_depth:
            return

        try:
            entries = list(current_path.iterdir())
        except PermissionError:
            return

        for entry in entries:
            if entry.is_symlink() and not follow_symlinks:
                continue
            if self._should_ignore(entry, ignore_patterns):
                continue

            if entry.is_file():
                file_type = self._get_file_type(entry)
                if file_type != FileType.UNKNOWN:
                    stat_info = entry.stat()
                    modified = stat_info.st_mtime
                    file_info = FileInfo(
                        path=entry,
                        file_type=file_type,
                        size=stat_info.st_size,
                        modified_time=datetime.fromtimestamp(modified, tz=timezone.utc).isoformat(),
                    )
                    results.append(file_info)
            elif entry.is_dir():
                self._scan_recursive(
                    entry,
                    max_depth,
                    follow_symlinks,
                    ignore_patterns,
                    results,
                    current_depth + 1,
                )

    def _should_ignore(self, path: Path, patterns: list[str]) -> bool:
        name = path.name
        for pattern in patterns:
            if pattern.startswith("."):
                if name == pattern or name.startswith(pattern + "/"):
                    return True
            if "*" in pattern:
                if fnmatch.fnmatch(name, pattern):
                    return True
            elif name == pattern:
                return True
        return False

    def _get_file_type(self, path: Path) -> FileType:
        ext = path.suffix.lower()
        return self.EXTENSION_MAP.get(ext, FileType.UNKNOWN)
