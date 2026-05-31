# Claude Handoff Template

Use this template when Codex prepares implementation work for Claude.

```md
# Claude Implementation Handoff

## Task ID

T-0000

## Task Title

...

## Goal

Describe the specific outcome Claude must implement.

## Business Reason

Explain why this matters for OmniVia.

## Task Lane

Tiny | Standard | High-risk

Use:

- Tiny for one-file changes, documentation cleanup, prompt/template edits, or narrow follow-up fixes.
- Standard for normal implementation tasks with bounded scope.
- High-risk for persistence, data model, MCP contracts, dependencies, architecture, cross-module changes, or anything that could corrupt user/project data.

## Context Budget

Bundle: Minimal | Planning | Implementation | Review

Use `/ops/CONTEXT_BUDGET.md`.

Read in full:

- AGENTS.md
- ...

Consult only if needed:

- ...

Do not load unless explicitly required:

- Raw chat exports
- Long command logs
- Generated files
- Dependency folders
- Broad documentation trees unrelated to this task

## Context Files to Read First

List the task-specific files Claude must read before changing code. Use the Context Budget section to narrow this list for tiny or standard tasks.

Default candidates:

- AGENTS.md
- /ops/CONTEXT_BUDGET.md
- /context/PROJECT_CONTEXT.md
- /context/PRODUCT_DECISIONS.md
- /context/ARCHITECTURE_NOTES.md
- /context/BUILD_RULES.md
- /ops/OPERATING_MODEL.md
- /ops/DECISION_LOG.md
- /ops/TASK_BACKLOG.md

## Repo Inspection Required

Before modifying files, inspect:

- Current repo structure
- Relevant source files
- Package manager and scripts
- Existing tests
- Existing patterns for naming, error handling, and configuration

## Files Likely In Scope

List likely files or folders.

## Files Out of Scope

List files or folders Claude must not modify.

## Implementation Instructions

1. ...
2. ...
3. ...

## Agent Mode

Recommended: Single session | Subagents only | Agent team

Use single session when:

- The task is small, sequential or concentrated in one module.
- Parallel work would create coordination overhead.

Use subagents only when:

- The lead Claude session should keep implementation ownership.
- Specialist support is useful for review, test planning, docs drift, MCP contracts or repo hygiene.

Use an agent team when:

- Work can be split into independent streams with clear file ownership.
- The lead Claude session can safely integrate results before final checks.

## Specialist Support

Relevant subagents:

- `omnivia-code-reviewer` for post-change review
- `omnivia-test-planner` for coverage planning
- `omnivia-docs-guard` for docs/spec/ADR/task drift checks
- `omnivia-mcp-specialist` for MCP tool and stdio server work
- `omnivia-repo-hygiene` before final status or commit

## Parallel Work Boundaries

Only fill this section when Agent Mode is Agent team.

- Work stream:
- Responsible teammate:
- Files in scope:
- Files out of scope:
- Integration owner:

Rules:

- Define each teammate's ownership and allowed files before implementation starts.
- Do not let multiple teammates edit the same files at the same time.
- Keep one teammate read-only when overlap is unavoidable.
- Wait for teammates to finish before integrating results.
- The lead Claude remains responsible for final tests, review reports, DoD and final response.

## Acceptance Criteria

- ...
- ...
- ...

## Required Checks

List exact commands. Do not use vague phrases like "run tests" or "lint passed."

```bash
# Example for services/omnivia-memory
cd services/omnivia-memory && python3 -m pytest -q
cd services/omnivia-memory && python3 -m ruff check src tests
cd services/omnivia-memory && python3 -m ruff format --check src tests
cd services/omnivia-memory && python3 -m mypy src
```

## Quality Evidence Required

Claude must include a table in the final response and DoD report:

| Check | Command | Result | Notes |
|---|---|---|---|
| Tests | ... | Pass/Fail/Not run | ... |
| Lint | ... | Pass/Fail/Not run | ... |
| Format | ... | Pass/Fail/Not run | ... |
| Typecheck | ... | Pass/Fail/Not run | ... |

## Definition of Done

- The requested behaviour is implemented or the blocker is clearly explained
- Relevant tests are added or updated where practical
- Existing tests pass or failures are explained
- Build and lint checks pass or failures are explained
- Exact required check commands and outputs are reported
- No unrelated files are modified
- No secrets or local environment files are committed
- Source files remain within the approved scope
- Ignored generated files and caches are cleaned from the task scope before final status or staging
- Final response lists changed files, checks run, and remaining risks

## Git Instructions

- Work on a feature branch if appropriate
- Inspect `git status` before committing
- Inspect the diff before committing
- If tests, formatters, linters or type checks create ignored generated files, clean them with a scoped command such as `git clean -fdX <changed-task-directory>` after confirming the directory
- Do not commit unless this handoff explicitly allows committing
- Commit only if Definition of Done passes and all required checks have been run or explicitly justified
- Use this commit message:

```text
T-0000: concise outcome-based message
```

## Final Response Required From Claude

Claude must report:

1. Summary of changes
2. Changed files
3. Checks run
4. Test results
5. Build or lint results
6. Risks or limitations
7. Whether a commit was created
8. Suggested follow-up tasks
```
