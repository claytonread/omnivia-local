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

## External Code Boundary

Do not import from `external/reference/`.
Do not copy code from external repositories into OmniVia implementation folders unless the user explicitly approves it and the dependency register permits it.

<!-- OMNIVIA_CODE_QUALITY_END -->
