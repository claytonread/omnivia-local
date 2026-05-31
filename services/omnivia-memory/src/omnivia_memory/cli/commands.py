"""Command-line interface for OmniVia memory operations.

Provides a basic CLI for creating, listing, retrieving, updating,
deleting, and searching memories. Also supports lifecycle transitions
(approve/reject).

Usage:
    omnivia-memory create --content "memory content" --source-type file --source-ref path/to/file.py
    omnivia-memory list
    omnivia-memory get <memory-id>
    omnivia-memory search "query"
    omnivia-memory approve <memory-id>
    omnivia-memory reject <memory-id>
"""

from __future__ import annotations

import argparse
import sys

from omnivia_memory.lifecycle.models import LifecycleState
from omnivia_memory.lifecycle.rules import CreatedBy
from omnivia_memory.memory.models import MemoryCreate, MemoryUpdate
from omnivia_memory.memory.service import (
    InvalidTransitionError,
    MemoryNotFoundError,
    MemoryService,
    MemoryServiceError,
)
from omnivia_memory.persistence.database import Database, DatabaseConfig
from omnivia_memory.persistence.repositories import MemoryRepository
from omnivia_memory.provenance.models import Source, SourceType


def create_memory_service() -> MemoryService:
    """Create a configured memory service with SQLite persistence.

    Returns:
        Configured MemoryService instance
    """
    from pathlib import Path

    # Use default database location
    home = Path.home()
    db_dir = home / ".omnivia"
    db_dir.mkdir(parents=True, exist_ok=True)
    db_path = db_dir / "memories.db"

    config = DatabaseConfig(db_path=db_path)
    db = Database(config)
    db.connect()

    repository = MemoryRepository(db)
    return MemoryService(repository=repository)


def format_memory(memory) -> str:
    """Format a memory for CLI output.

    Args:
        memory: Memory object to format

    Returns:
        Formatted string representation
    """
    return f"""Memory: {memory.id}
Content: {memory.content}
Source: [{memory.source.type.value}] {memory.source.reference}
  Description: {memory.source.description or "N/A"}
State: {memory.lifecycle_state.value}
Type: {memory.memory_type}
Created by: {memory.created_by.value}
Created: {memory.created_at}
Updated: {memory.updated_at}"""


def cmd_create(args: argparse.Namespace) -> int:
    """Handle memory creation command.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        service = create_memory_service()

        # Parse source type
        source_type_map = {
            "file": SourceType.FILE,
            "url": SourceType.URL,
            "adr": SourceType.ADR,
            "human": SourceType.HUMAN,
        }
        source_type = source_type_map.get(args.source_type)
        if source_type is None:
            print(f"Error: Invalid source type '{args.source_type}'", file=sys.stderr)
            print("Valid types: file, url, adr, human", file=sys.stderr)
            return 1

        # Parse creator type
        created_by_map = {"human": CreatedBy.HUMAN, "agent": CreatedBy.AGENT}
        created_by = created_by_map.get(args.created_by, CreatedBy.AGENT)

        source = Source(
            type=source_type,
            reference=args.source_ref,
            description=args.source_desc,
        )

        memory_input = MemoryCreate(
            content=args.content,
            source=source,
            memory_type=args.memory_type or "general",
            created_by=created_by,
        )

        memory = service.create(memory_input)
        print(f"Created memory: {memory.id}")
        print(format_memory(memory))
        return 0

    except MemoryServiceError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_list(args: argparse.Namespace) -> int:
    """Handle memory listing command.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        service = create_memory_service()

        # Filter by lifecycle state if specified
        state_filter = None
        if args.state:
            try:
                state_filter = LifecycleState(args.state)
            except ValueError:
                print(f"Error: Invalid lifecycle state '{args.state}'", file=sys.stderr)
                print("Valid states: proposed, observed, approved, rejected", file=sys.stderr)
                return 1

        memories = service.list(
            limit=args.limit or 100,
            offset=args.offset or 0,
            lifecycle_state=state_filter,
        )

        if not memories:
            print("No memories found.")
            return 0

        print(f"Found {len(memories)} memory(ies):\n")
        for memory in memories:
            print(format_memory(memory))
            print("-" * 60)
        return 0

    except MemoryServiceError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_get(args: argparse.Namespace) -> int:
    """Handle memory retrieval command.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        service = create_memory_service()
        memory = service.get(args.memory_id)
        print(format_memory(memory))
        return 0

    except MemoryNotFoundError:
        print(f"Error: Memory '{args.memory_id}' not found", file=sys.stderr)
        return 1
    except MemoryServiceError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_update(args: argparse.Namespace) -> int:
    """Handle memory update command.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        service = create_memory_service()

        update_input = MemoryUpdate(
            content=args.content,
            memory_type=args.memory_type,
        )

        memory = service.update(args.memory_id, update_input)
        print(f"Updated memory: {memory.id}")
        print(format_memory(memory))
        return 0

    except MemoryNotFoundError:
        print(f"Error: Memory '{args.memory_id}' not found", file=sys.stderr)
        return 1
    except InvalidTransitionError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except MemoryServiceError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_delete(args: argparse.Namespace) -> int:
    """Handle memory deletion command.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        service = create_memory_service()
        deleted = service.delete(args.memory_id)

        if deleted:
            print(f"Deleted memory: {args.memory_id}")
            return 0
        else:
            print(f"Error: Memory '{args.memory_id}' not found", file=sys.stderr)
            return 1

    except MemoryServiceError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_search(args: argparse.Namespace) -> int:
    """Handle memory search command.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        service = create_memory_service()
        memories = service.search(args.query, limit=args.limit or 20)

        if not memories:
            print(f"No memories found matching: {args.query}")
            return 0

        print(f"Found {len(memories)} matching memory(ies):\n")
        for memory in memories:
            print(format_memory(memory))
            print("-" * 60)
        return 0

    except MemoryServiceError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_approve(args: argparse.Namespace) -> int:
    """Handle memory approval command.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        service = create_memory_service()
        memory = service.approve(args.memory_id)
        print(f"Approved memory: {memory.id}")
        print(format_memory(memory))
        return 0

    except MemoryNotFoundError:
        print(f"Error: Memory '{args.memory_id}' not found", file=sys.stderr)
        return 1
    except InvalidTransitionError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except MemoryServiceError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_reject(args: argparse.Namespace) -> int:
    """Handle memory rejection command.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        service = create_memory_service()
        memory = service.reject(args.memory_id)
        print(f"Rejected memory: {memory.id}")
        print(format_memory(memory))
        return 0

    except MemoryNotFoundError:
        print(f"Error: Memory '{args.memory_id}' not found", file=sys.stderr)
        return 1
    except InvalidTransitionError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except MemoryServiceError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_stats(args: argparse.Namespace) -> int:
    """Handle memory statistics command.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        service = create_memory_service()
        stats = service.get_stats()

        print("Memory Statistics:")
        print(f"  Total memories: {stats['total']}")
        if "by_state" in stats:
            print("  By state:")
            for state, count in stats["by_state"].items():
                print(f"    {state}: {count}")
        return 0

    except MemoryServiceError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the CLI.

    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        prog="omnivia-memory",
        description="OmniVia Dev memory operations CLI",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # create command
    create_parser = subparsers.add_parser("create", help="Create a new memory")
    create_parser.add_argument("--content", required=True, help="Memory content")
    create_parser.add_argument(
        "--source-type",
        required=True,
        choices=["file", "url", "adr", "human"],
        help="Source type",
    )
    create_parser.add_argument("--source-ref", required=True, help="Source reference")
    create_parser.add_argument("--source-desc", help="Source description (optional)")
    create_parser.add_argument("--memory-type", help="Memory type (default: general)")
    create_parser.add_argument(
        "--created-by",
        default="agent",
        choices=["human", "agent"],
        help="Who created this memory (default: agent)",
    )
    create_parser.set_defaults(func=cmd_create)

    # list command
    list_parser = subparsers.add_parser("list", help="List memories")
    list_parser.add_argument("--limit", type=int, help="Maximum number to return")
    list_parser.add_argument("--offset", type=int, help="Number to skip")
    list_parser.add_argument(
        "--state",
        choices=["proposed", "observed", "approved", "rejected"],
        help="Filter by lifecycle state",
    )
    list_parser.set_defaults(func=cmd_list)

    # get command
    get_parser = subparsers.add_parser("get", help="Get a memory by ID")
    get_parser.add_argument("memory_id", help="Memory ID")
    get_parser.set_defaults(func=cmd_get)

    # update command
    update_parser = subparsers.add_parser("update", help="Update a memory")
    update_parser.add_argument("memory_id", help="Memory ID")
    update_parser.add_argument("--content", help="New content")
    update_parser.add_argument("--memory-type", help="New memory type")
    update_parser.set_defaults(func=cmd_update)

    # delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a memory")
    delete_parser.add_argument("memory_id", help="Memory ID")
    delete_parser.set_defaults(func=cmd_delete)

    # search command
    search_parser = subparsers.add_parser("search", help="Search memories")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--limit", type=int, help="Maximum results")
    search_parser.set_defaults(func=cmd_search)

    # approve command
    approve_parser = subparsers.add_parser("approve", help="Approve a memory")
    approve_parser.add_argument("memory_id", help="Memory ID")
    approve_parser.set_defaults(func=cmd_approve)

    # reject command
    reject_parser = subparsers.add_parser("reject", help="Reject a memory")
    reject_parser.add_argument("memory_id", help="Memory ID")
    reject_parser.set_defaults(func=cmd_reject)

    # stats command
    stats_parser = subparsers.add_parser("stats", help="Show memory statistics")
    stats_parser.set_defaults(func=cmd_stats)

    return parser


def main() -> int:
    """Main entry point for the CLI.

    Returns:
        Exit code
    """
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
