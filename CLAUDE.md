# OmniVia Claude Instructions

You are working on OmniVia.

OmniVia is a local-first, cloud-scalable, governed business knowledge and agent memory layer.

OmniVia is not the SMB OS. MotuVia is the SMB OS. SanaVia is the allied health vertical product. AltaVia is the parent company and AI consultancy.

## External Repo Rules

The folder `external/reference/` contains third-party repositories for review only.

Do not copy code from `external/reference/` into OmniVia implementation folders.

Do not vendor code.

Do not import from `external/reference/`.

Only review, classify, recommend and update documentation/spec files.

OmniVia-owned code belongs in:

- `services/`
- `apps/`
- `packages/`
- `infra/`
- `features/`
- `specs/`

Third-party reference code belongs in:

- `external/reference/`

## Required Output Behaviour

When asked to review open source repos, create documentation in `docs/open-source/`.

Do not edit implementation code unless explicitly asked later.

<!-- OMNIVIA_CODE_QUALITY_START -->

# OmniVia Code Quality and Commenting Rules

These rules apply to all OmniVia code going forward.

## Plain-English Commenting Standard

Claude must write code that a non-expert product owner can understand.

When adding or changing code:

1. Add clear comments that explain why the code exists, not just what it does.
2. Use layman-friendly language where possible.
3. Explain domain logic, memory lifecycle logic, source-backed retrieval logic, agent permission logic and governance rules.
4. Add comments before complex blocks.
5. Add comments to tricky lines when the line is not obvious to a junior developer.
6. Do not comment obvious boilerplate unless it helps orientation.
7. Do not leave vague comments like "handle data" or "process stuff".
8. Do not hide unclear code behind comments. If code is confusing, simplify it first.
9. Public functions, service methods, MCP tools and API handlers must have short docstrings or equivalent documentation.
10. Any safety, permission, status transition or data-loss behaviour must be commented clearly.

## Required Comment Style

Good comment:

```python
# Agent-created memories start as "proposed" so the AI cannot silently turn
# an unverified observation into approved business truth.
approval_status = "proposed"
```

Bad comment:

```python
# Set status
approval_status = "proposed"
```

## Code Review Standard

Before claiming an implementation task is complete, Claude must perform a peer-review pass.

The peer review must check:

1. Correctness
2. Simplicity
3. Readability
4. Comments and docstrings
5. Error handling
6. Tests
7. Security and permissions
8. Data persistence
9. Source references
10. Agent safety
11. Alignment to OmniVia specs
12. Avoidance of external/reference code imports

## Completion Protocol

Before saying "done", Claude must:

1. Run a comment pass over changed code.
2. Run a peer-review pass over changed code.
3. Run available tests or explain why tests could not be run.
4. Create or update a review report in `docs/quality/reviews/`.
5. Summarise remaining risks and next actions.

## Lessons Learned Rule

Claude must record durable lessons only when they change how future OmniVia work should be done.

Record reusable lessons about:

1. Process or Definition of Done gaps.
2. Tooling commands and check scope.
3. SDK behaviour that affects implementation correctness.
4. Architecture or data model constraints.
5. Repo hygiene and generated-file cleanup.

Use the most appropriate durable location:

- `CLAUDE.md` for future Claude behaviour rules.
- `ops/DECISION_LOG.md` for accepted product or architecture decisions.
- `ops/TASK_BACKLOG.md` for follow-up work.
- `docs/quality/reviews/` for task-specific review findings.

Do not record raw scratch notes, one-off mistakes, implementation diary entries, or raw chat transcripts.

## Python Service Check Rule

For Python services, Claude must run checks across both source and tests where applicable:

```bash
python3 -m pytest -q
python3 -m ruff check src tests
python3 -m ruff format --check src tests
python3 -m mypy src
```

Do not report a check as passed unless the exact command was run and the output supports it. If a check is intentionally scoped, say exactly what was checked and why broader coverage was not run.

## External Code Boundary

Do not import from `external/reference/`.
Do not copy code from external repositories into OmniVia implementation folders unless the user explicitly approves it and the dependency register permits it.

## Agent Team Rules

Claude Code agent teams are enabled for OmniVia and should be considered when work can be safely parallelised.

Project-specific subagents are available under `.claude/agents/`. Use them to keep specialist research and review out of the lead implementation context.

Use these subagents where relevant:

1. `omnivia-code-reviewer` for post-change implementation review and DoD readiness.
2. `omnivia-test-planner` before or during implementation when test coverage needs to be designed.
3. `omnivia-docs-guard` when behaviour, scope, architecture, tasks, specs, ADRs or MCP contracts may require documentation updates.
4. `omnivia-mcp-specialist` for MCP server, MCP tool contract, stdio transport and agent-safety work.
5. `omnivia-repo-hygiene` before final status or commit to inspect git status, ignored generated files and cleanup scope.

Use an agent team when:

1. Work has independent slices that can be owned by separate teammates.
2. Parallel research or review would improve quality.
3. Cross-layer work can be split by clear boundaries, such as implementation, tests and documentation.
4. Debugging benefits from competing hypotheses.

Do not use an agent team when:

1. The task is sequential or small enough for one session.
2. Multiple teammates would edit the same files or same module at the same time.
3. The task requires unresolved product or architecture decisions.
4. The user or Codex asked for a single bounded implementation pass.

When using an agent team:

1. The lead must create clear task ownership and file boundaries before implementation starts.
2. Teammates must read the same task handoff and relevant OmniVia docs.
3. Require plan approval for risky teammates before they make changes.
4. Prefer research and review teams before parallel implementation.
5. Wait for teammates to finish before synthesising results or claiming completion.
6. The lead is responsible for final integration, tests, review reports and DoD.
7. The lead must clean up the team when work is complete.

<!-- OMNIVIA_CODE_QUALITY_END -->

<!-- OMNIVIA_DEFINITION_OF_DONE_START -->

# OmniVia Definition of Done Rules

These rules apply to every OmniVia implementation task.

## Definition of Done

A task is not done until all of the following are true:

1. The implementation satisfies the relevant spec acceptance criteria.
2. The implementation has been tested, or the reason tests could not be run is documented.
3. The changed code has completed the comment pass.
4. The changed code has completed peer review.
5. Critical and High review findings are fixed or explicitly accepted by the user.
6. Relevant documentation has been updated.
7. Relevant specs, plans or tasks have been updated if the behaviour changed.
8. Relevant ADRs have been added or updated if an architecture decision changed.
9. API, MCP or data model contracts have been updated if interfaces changed.
10. The dependency register has been updated if dependencies changed.
11. The implementation does not import from `external/reference/`.
12. Agent-created knowledge defaults to proposed where applicable.
13. Source references, audit logging and permission checks are preserved where applicable.
14. Ignored generated files and caches created by checks have been removed from the task scope before final status or staging.
15. The final response includes:
    - what changed
    - tests run
    - review result
    - docs/specs updated
    - remaining risks
    - exact commands to run

## Documentation Update Rule

Claude must update documentation when a task changes:

- setup commands
- API behaviour
- MCP tools
- data models
- environment variables
- Docker services
- test commands
- architecture decisions
- user workflow
- onboarding instructions
- known limitations

## Spec Update Rule

Claude must update specs, plans or tasks when implementation reveals:

- a new requirement
- a changed requirement
- a removed requirement
- an acceptance criterion that is no longer valid
- a new dependency
- a changed interface
- a new risk or constraint
- a change in product behaviour

## Final Gate

Before saying a task is complete, Claude must run the DoD check in:

`.claude/commands/dod-check.md`

<!-- OMNIVIA_DEFINITION_OF_DONE_END -->

<!-- OMNIVIA_AUTOMATIC_FINISH_GATE_START -->

# OmniVia Automatic Finish Gate

Claude Code has an OmniVia Stop/TaskCompleted hook installed.

When code or configuration files change, Claude must not consider the task complete until:

1. `.claude/commands/finish-task.md` has been followed.
2. Comment pass has been completed.
3. Peer review report exists in `docs/quality/reviews/`.
4. Definition of Done report exists in `docs/quality/reviews/`.
5. Tests have been run or manual validation is documented.
6. Critical and High findings are fixed or explicitly accepted.
7. Relevant docs, specs, tasks, ADRs and dependency registers are updated.
8. Ignored generated files and caches in the changed task scope have been cleaned or confirmed ignored before final status or staging.

Use a scoped ignored-file cleanup command such as `git clean -fdX <changed-task-directory>` only after confirming the target directory. Do not run broad cleanup commands outside the task scope unless explicitly instructed.

If the hook blocks completion, read the hook reason and continue working.

<!-- OMNIVIA_AUTOMATIC_FINISH_GATE_END -->
