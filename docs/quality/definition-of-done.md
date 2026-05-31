# OmniVia Definition of Done

A task, feature or implementation slice is only done when it is working, reviewed, documented and aligned to the relevant OmniVia specs.

## Mandatory Completion Criteria

### 1. Spec Alignment

- The implementation satisfies the relevant spec.
- Acceptance criteria have been checked.
- If implementation changed intended behaviour, the spec was updated.
- If requirements changed, tasks were updated.

### 2. Code Quality

- Code is readable.
- Complex logic is commented in plain English.
- Public functions, API handlers, service methods and MCP tools have docstrings or equivalent explanation.
- No unnecessary complexity was introduced.
- No code imports from `external/reference/`.

### 3. Tests and Validation

- Relevant automated tests pass.
- If no tests exist, a manual validation path is documented.
- Smoke test commands are provided.
- Failure cases are considered.

### 4. Agent Safety

- Agent-created memories default to proposed where applicable.
- Agent actions are logged where applicable.
- Restricted or rejected knowledge is not returned in normal recall.
- Permission checks are preserved where applicable.

### 5. Source-Backed Knowledge

- Source references are preserved where relevant.
- Retrieval results include source context where relevant.
- Inferred knowledge is not presented as approved truth.

### 6. Documentation

Update documentation when changed behaviour affects:

- setup
- runtime commands
- API endpoints
- MCP tools
- data models
- environment variables
- Docker services
- tests
- architecture
- user workflows
- known limitations

### 7. Architecture Decisions

Create or update an ADR when the task changes:

- database choice
- package choice
- service boundary
- runtime architecture
- agent interface
- data model
- deployment model
- security model
- licence posture

### 8. Review Evidence

A peer review report must exist in:

`docs/quality/reviews/`

The report must include:

- files reviewed
- findings
- tests run
- decision
- remaining risks

### 9. Generated File Cleanup

- Ignored generated files and caches created by tests, type checks, formatters or linters are removed from the task scope before final status or staging.
- Cleanup commands must be scoped to the changed task directory, for example `git clean -fdX services/omnivia-memory`.
- Do not run broad cleanup commands outside the task scope unless explicitly instructed.

## Final Task Summary Required

Every completed task must end with:

```markdown
## Completion Summary

### What Changed

### Tests Run

### Review Result

### Documentation Updated

### Specs or Tasks Updated

### Remaining Risks

### Commands to Run
```
