"""Tests for the lifecycle module."""

from omnivia_memory.lifecycle.models import LifecycleState
from omnivia_memory.lifecycle.rules import CreatedBy, LifecycleRules


class TestLifecycleState:
    """Tests for LifecycleState enum."""

    def test_lifecycle_state_values(self):
        """LifecycleState has expected values."""
        assert LifecycleState.PROPOSED == "proposed"
        assert LifecycleState.OBSERVED == "observed"
        assert LifecycleState.APPROVED == "approved"
        assert LifecycleState.REJECTED == "rejected"

    def test_proposed_can_transition_to_observed(self):
        """Proposed can transition to observed."""
        assert LifecycleState.PROPOSED.can_transition_to(LifecycleState.OBSERVED)

    def test_proposed_can_transition_to_approved(self):
        """Proposed can transition to approved (with human approval)."""
        assert LifecycleState.PROPOSED.can_transition_to(LifecycleState.APPROVED)

    def test_proposed_can_transition_to_rejected(self):
        """Proposed can transition to rejected."""
        assert LifecycleState.PROPOSED.can_transition_to(LifecycleState.REJECTED)

    def test_proposed_cannot_transition_to_proposed(self):
        """Proposed cannot stay in proposed (no self-loop)."""
        assert not LifecycleState.PROPOSED.can_transition_to(LifecycleState.PROPOSED)

    def test_observed_can_transition_to_approved(self):
        """Observed can transition to approved."""
        assert LifecycleState.OBSERVED.can_transition_to(LifecycleState.APPROVED)

    def test_observed_can_transition_to_rejected(self):
        """Observed can transition to rejected."""
        assert LifecycleState.OBSERVED.can_transition_to(LifecycleState.REJECTED)

    def test_observed_cannot_transition_to_proposed(self):
        """Observed cannot go back to proposed."""
        assert not LifecycleState.OBSERVED.can_transition_to(LifecycleState.PROPOSED)

    def test_approved_can_transition_to_rejected(self):
        """Approved can be rejected (retraction)."""
        assert LifecycleState.APPROVED.can_transition_to(LifecycleState.REJECTED)

    def test_approved_cannot_transition_to_approved(self):
        """Approved cannot stay in approved (no self-loop)."""
        assert not LifecycleState.APPROVED.can_transition_to(LifecycleState.APPROVED)

    def test_rejected_is_terminal(self):
        """Rejected is a terminal state."""
        assert LifecycleState.REJECTED.is_terminal()

    def test_rejected_cannot_transition(self):
        """Rejected cannot transition to any state."""
        for state in LifecycleState:
            assert not LifecycleState.REJECTED.can_transition_to(state)

    def test_approved_is_approved_state(self):
        """Approved is the approved state."""
        assert LifecycleState.APPROVED.is_approved()

    def test_proposed_requires_human_approval(self):
        """Proposed requires human approval to become approved."""
        assert LifecycleState.PROPOSED.requires_human_approval_to_approve()

    def test_observed_does_not_require_human_approval(self):
        """Observed does not require human approval."""
        # Observed can proceed to approved after more evidence
        assert not LifecycleState.OBSERVED.requires_human_approval_to_approve()


class TestLifecycleRules:
    """Tests for LifecycleRules class."""

    def test_human_created_starts_approved(self):
        """Human-created memories start as approved."""
        initial = LifecycleRules.get_initial_state(CreatedBy.HUMAN)
        assert initial == LifecycleState.APPROVED

    def test_agent_created_starts_proposed(self):
        """Agent-created memories start as proposed."""
        initial = LifecycleRules.get_initial_state(CreatedBy.AGENT)
        assert initial == LifecycleState.PROPOSED

    def test_can_transition_valid(self):
        """Valid transitions return True."""
        assert LifecycleRules.can_transition(
            LifecycleState.PROPOSED,
            LifecycleState.APPROVED,
        )

    def test_can_transition_invalid(self):
        """Invalid transitions return False."""
        assert not LifecycleRules.can_transition(
            LifecycleState.REJECTED,
            LifecycleState.APPROVED,
        )

    def test_requires_human_approval_from_proposed(self):
        """Proposed requires human approval."""
        assert LifecycleRules.requires_human_approval(LifecycleState.PROPOSED)

    def test_requires_human_approval_from_observed(self):
        """Observed does not require human approval."""
        assert not LifecycleRules.requires_human_approval(LifecycleState.OBSERVED)

    def test_is_approved_state(self):
        """is_approved_state returns True for approved."""
        assert LifecycleRules.is_approved_state(LifecycleState.APPROVED)

    def test_is_terminal_state_rejected(self):
        """Rejected is a terminal state."""
        assert LifecycleRules.is_terminal_state(LifecycleState.REJECTED)

    def test_is_not_terminal_state_proposed(self):
        """Proposed is not a terminal state."""
        assert not LifecycleRules.is_terminal_state(LifecycleState.PROPOSED)
