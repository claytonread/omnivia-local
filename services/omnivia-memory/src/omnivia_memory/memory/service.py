"""Memory service layer.

Provides high-level operations for memory management including
CRUD operations and lifecycle transitions.
"""

from __future__ import annotations

from typing import Any

from omnivia_memory.lifecycle.models import LifecycleState
from omnivia_memory.lifecycle.rules import LifecycleRules
from omnivia_memory.memory.models import Memory, MemoryCreate, MemoryUpdate
from omnivia_memory.persistence.repositories import MemoryRepository
from omnivia_memory.search.service import SearchService


class MemoryServiceError(Exception):
    """Base exception for memory service errors."""

    pass


class MemoryNotFoundError(MemoryServiceError):
    """Raised when a requested memory does not exist."""

    pass


class InvalidTransitionError(MemoryServiceError):
    """Raised when a lifecycle transition is not allowed."""

    pass


class MemoryService:
    """High-level service for memory operations.

    Provides the main interface for managing memories, including:
    - Creating, retrieving, updating, and deleting memories
    - Lifecycle transitions (approve, reject, observe)
    - Keyword search

    Attributes:
        repository: The repository for persistence
        search_service: The service for keyword search
    """

    def __init__(
        self,
        repository: MemoryRepository | None = None,
        search_service: SearchService | None = None,
    ) -> None:
        self.repository = repository
        self.search_service = search_service or SearchService()

    def create(self, input_data: MemoryCreate) -> Memory:
        """Create and store a new memory.

        The memory is assigned an initial lifecycle state based on
        whether it was created by a human or agent.

        Args:
            input_data: The memory creation input

        Returns:
            The created memory
        """
        memory = input_data.to_memory()
        if self.repository:
            self.repository.create(memory)
        return memory

    def get(self, memory_id: str) -> Memory:
        """Retrieve a memory by ID.

        Args:
            memory_id: The unique identifier of the memory

        Returns:
            The memory

        Raises:
            MemoryNotFoundError: If the memory doesn't exist
        """
        if not self.repository:
            raise MemoryServiceError("Repository not configured")

        memory = self.repository.get_by_id(memory_id)
        if memory is None:
            raise MemoryNotFoundError(f"Memory {memory_id} not found")
        return memory

    def list(
        self,
        limit: int = 100,
        offset: int = 0,
        lifecycle_state: LifecycleState | None = None,
    ) -> list[Memory]:
        """List memories with optional filtering.

        Args:
            limit: Maximum number of memories to return
            offset: Number of memories to skip
            lifecycle_state: Optional filter by lifecycle state

        Returns:
            List of memories matching the criteria
        """
        if not self.repository:
            raise MemoryServiceError("Repository not configured")

        return self.repository.list_all(
            limit=limit,
            offset=offset,
            lifecycle_state=lifecycle_state,
        )

    def update(self, memory_id: str, input_data: MemoryUpdate) -> Memory:
        """Update an existing memory.

        Args:
            memory_id: The ID of the memory to update
            input_data: The update input

        Returns:
            The updated memory

        Raises:
            MemoryNotFoundError: If the memory doesn't exist
        """
        if not self.repository:
            raise MemoryServiceError("Repository not configured")

        memory = self.get(memory_id)

        # If updating lifecycle state, validate the transition
        if input_data.lifecycle_state is not None:
            if not LifecycleRules.can_transition(
                memory.lifecycle_state,
                input_data.lifecycle_state,
            ):
                raise InvalidTransitionError(
                    f"Cannot transition from {memory.lifecycle_state.value} "
                    f"to {input_data.lifecycle_state.value}"
                )

        input_data.apply_to(memory)

        if self.repository:
            self.repository.update(memory)

        return memory

    def delete(self, memory_id: str) -> bool:
        """Delete a memory.

        Args:
            memory_id: The ID of the memory to delete

        Returns:
            True if the memory was deleted

        Raises:
            MemoryNotFoundError: If the memory doesn't exist
        """
        if not self.repository:
            raise MemoryServiceError("Repository not configured")

        # Verify memory exists
        self.get(memory_id)

        return self.repository.delete(memory_id)

    def search(self, query: str, limit: int = 20) -> list[Memory]:
        """Search memories by keyword.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of matching memories
        """
        if not self.repository:
            raise MemoryServiceError("Repository not configured")

        return self.repository.search(query, limit)

    def approve(self, memory_id: str) -> Memory:
        """Approve a memory (transition to approved state).

        Human approval moves proposed or observed memories to approved.

        Args:
            memory_id: The ID of the memory to approve

        Returns:
            The approved memory

        Raises:
            MemoryNotFoundError: If the memory doesn't exist
            InvalidTransitionError: If the memory cannot be approved
        """
        memory = self.get(memory_id)

        if not LifecycleRules.can_transition(
            memory.lifecycle_state,
            LifecycleState.APPROVED,
        ):
            raise InvalidTransitionError(
                f"Cannot approve memory in {memory.lifecycle_state.value} state"
            )

        memory.transition_to(LifecycleState.APPROVED)

        if self.repository:
            self.repository.update(memory)

        return memory

    def reject(self, memory_id: str) -> Memory:
        """Reject a memory.

        Any non-rejected memory can be rejected.

        Args:
            memory_id: The ID of the memory to reject

        Returns:
            The rejected memory

        Raises:
            MemoryNotFoundError: If the memory doesn't exist
            InvalidTransitionError: If the memory cannot be rejected
        """
        memory = self.get(memory_id)

        if not LifecycleRules.can_transition(
            memory.lifecycle_state,
            LifecycleState.REJECTED,
        ):
            raise InvalidTransitionError(
                f"Cannot reject memory in {memory.lifecycle_state.value} state"
            )

        memory.transition_to(LifecycleState.REJECTED)

        if self.repository:
            self.repository.update(memory)

        return memory

    def observe(self, memory_id: str) -> Memory:
        """Mark a memory as observed (partially validated).

        Only proposed memories can be observed.

        Args:
            memory_id: The ID of the memory to mark as observed

        Returns:
            The observed memory

        Raises:
            MemoryNotFoundError: If the memory doesn't exist
            InvalidTransitionError: If the memory cannot be observed
        """
        memory = self.get(memory_id)

        if not LifecycleRules.can_transition(
            memory.lifecycle_state,
            LifecycleState.OBSERVED,
        ):
            raise InvalidTransitionError(
                f"Cannot mark memory in {memory.lifecycle_state.value} state as observed"
            )

        memory.transition_to(LifecycleState.OBSERVED)

        if self.repository:
            self.repository.update(memory)

        return memory

    def get_stats(self) -> dict[str, Any]:
        """Get statistics about stored memories.

        Returns:
            Dictionary with counts by lifecycle state and total
        """
        if not self.repository:
            return {"total": 0}

        total = self.repository.count()
        by_state = {}
        for state in LifecycleState:
            by_state[state.value] = self.repository.count(state)

        return {
            "total": total,
            "by_state": by_state,
        }
