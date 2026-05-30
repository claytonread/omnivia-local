# OmniVia Claude Review Workflow

This document establishes the review process for Claude-generated commits and branches.

## When To Review

Review Claude output when:

1. **Commit to main** — After each implementation task, before pushing to main
2. **Feature branch PR** — When Claude creates a branch for a larger change
3. **Before critical changes** — When modifying core services, data models, or security-related code
4. **On user request** — When the user explicitly asks to review

## Review Triggers

### Automatic Review Triggers

Claude should initiate a self-review before committing when:
- The change touches multiple services
- The change modifies a database model
- The change introduces a new external dependency
- The change affects API contracts
- The task is marked "Review" in the task backlog

### User-Initiated Reviews

Use `/review` in Claude Code to trigger a review:
```
/review
```
This invokes the review workflow documented in `ops/REVIEW_CHECKLIST.md`.

## Review Process

### Step 1: Collect Context

Before reviewing:
```bash
# Get task details
cat ops/TASK_BACKLOG.md

# Get the diff
git diff HEAD~1

# Get commit message
git log -1 --stat

# Run checks
ruff check services/
pytest services/api/tests/
```

### Step 2: Apply Review Checklist

Use `ops/REVIEW_CHECKLIST.md` to evaluate:
- Product Fit
- Architecture Alignment
- Scope Control
- Code Quality
- Tests and Checks
- Security and Safety
- Git Hygiene

### Step 3: Document Findings

Fill out the review output format from `ops/REVIEW_CHECKLIST.md`:

```md
# Codex Review

## Recommendation
[Accept | Accept with follow-up tasks | Amend | Rework | Revert | Blocked]

## Summary
[One-paragraph summary of the change]

## What Looks Good
- [Specific positive observations]

## Issues Found
- [Specific issues, if any]

## Required Changes
- [Changes required before merge, if any]

## Suggested Follow-Up Tasks
- [Future improvements, if any]

## Checks Reviewed
- Tests: [result]
- Lint: [result]
- Build: [result]

## Merge Readiness
[Ready | Not ready]
```

### Step 4: Decide

Based on findings, choose:

| Decision | When |
|----------|------|
| **Accept** | All checks pass, no issues found |
| **Accept with follow-up** | Minor issues, can be addressed later |
| **Amend** | Small fixes needed before merge |
| **Rework** | Significant changes needed |
| **Revert** | Change is wrong or harmful |
| **Blocked** | Waiting on decision or dependency |

## Post-Review Actions

### If Accept

```bash
git push origin main
```

### If Amend

```bash
# Make fixes
git add .
git commit --amend
git push --force-with-lease
```

### If Rework

```bash
# Keep branch open, create new task
git checkout -b feature/T-NNNN-fix-issue
```

### If Revert

```bash
git revert HEAD
git push origin main
```

## Review Quality Standards

Good reviews are:
- **Specific** — Point to exact lines or patterns, not vague criticism
- **Constructive** — Suggest alternatives, not just problems
- **Practical** — Focus on real issues, not style preferences
- **Timely** — Review promptly to maintain momentum

Avoid:
- Bikeshedding on formatting (use ruff/ruff format instead)
- Nitpicking without actionable feedback
- Blocking on minor issues when main intent is sound
- Overlooking systemic issues that affect multiple commits

## Tracking Review State

After review, update the task backlog:

| Status | Meaning |
|--------|---------|
| Ready | Reviewed, cleared for implementation |
| In Progress | Currently being implemented |
| Review | Implementation done, needs review |
| Done | Reviewed and accepted |
| Blocked | Waiting on decision or dependency |

## Example Review: T-0004 (Domain Model)

```md
# Codex Review — T-0004: Define local knowledge domain model

## Recommendation
Accept

## Summary
Added Node and Edge models to the API, with basic CRUD endpoints and an ADR documenting the domain model evolution from Memory-only to graph-based.

## What Looks Good
- ADR clearly documents the three-phase evolution path
- Node/Edge models match the Architecture Notes
- Provenance tracking via source_ids is preserved
- Edge creation validates both nodes exist
- Tests still pass after model changes
- Commit is focused on domain model only

## Issues Found
None

## Required Changes
None

## Suggested Follow-Up Tasks
- Add NodeService and EdgeService classes (similar to MemoryService)
- Add tests for Node and Edge CRUD
- Consider adding a graph traversal endpoint

## Checks Reviewed
- Tests: 18/18 passed
- Lint: All checks passed
- Build: Docker build successful

## Merge Readiness
Ready
```

## Quick Reference

| Command | Purpose |
|---------|---------|
| `/review` | Invoke review workflow |
| `git diff HEAD~1` | See last commit changes |
| `git log --oneline -5` | Recent commits |
| `ruff check services/` | Run lint check |
| `pytest services/` | Run tests |