# DoD Spec Update Summary

Date: 2026-05-31
Command: `.claude/commands/update-dod-docs.md`
Source files: `docs/quality/definition-of-done.md`, `docs/quality/test-strategy.md`, `docs/templates/task-dod-template.md`

## Files Changed

### Specs (specs/)

| File | Change |
|------|--------|
| `001-local-runtime/specify.md` | Added DoD section |
| `001-local-runtime/plan.md` | Added DoD section |
| `002-memory-engine/specify.md` | Added DoD section |
| `002-memory-engine/plan.md` | Added DoD section |
| `003-agent-interface/specify.md` | Added DoD section |
| `003-agent-interface/plan.md` | Added DoD section |
| `004-ingestion-normalisation/specify.md` | Added DoD section |
| `004-ingestion-normalisation/plan.md` | Added DoD section |
| `005-vector-search/specify.md` | Added DoD section |
| `005-vector-search/plan.md` | Added DoD section |
| `006-governance-trust/specify.md` | Added DoD section |
| `006-governance-trust/plan.md` | Added DoD section |
| `007-knowledge-graph/specify.md` | Added DoD section |
| `007-knowledge-graph/plan.md` | Added DoD section |
| `008-workspace-ui/specify.md` | Added DoD section |
| `008-workspace-ui/plan.md` | Added DoD section |
| `009-connectors/specify.md` | Added DoD section |
| `009-connectors/plan.md` | Added DoD section |
| `010-cloud-sync/specify.md` | Added DoD section |
| `010-cloud-sync/plan.md` | Added DoD section |

**Total: 20 spec/plan files updated**

### Features (features/)

| File | Change |
|------|--------|
| `001-local-runtime/plan.md` | Added DoD section |
| `002-memory-engine/plan.md` | Added DoD section |
| `003-agent-interface/plan.md` | Added DoD section |
| `004-ingestion-normalisation/plan.md` | Added DoD section |
| `004-ingestion-normalisation/spec.md` | Added DoD section |
| `005-vector-search/plan.md` | Added DoD section |
| `005-vector-search/spec.md` | Added DoD section |
| `006-governance-trust/plan.md` | Added DoD section |
| `006-governance-trust/spec.md` | Added DoD section |
| `007-knowledge-graph/plan.md` | Added DoD section |
| `007-knowledge-graph/spec.md` | Added DoD section |
| `008-workspace-ui/plan.md` | Added DoD section |
| `008-workspace-ui/spec.md` | Added DoD section |
| `009-connectors/plan.md` | Added DoD section |
| `009-connectors/spec.md` | Added DoD section |
| `010-cloud-sync/plan.md` | Added DoD section |
| `010-cloud-sync/spec.md` | Added DoD section |

**Total: 17 feature spec/plan files updated**

### ADRs (docs/adr/)

| File | Change |
|------|--------|
| `ADR-001-qdrant-mvp-vector-database.md` | Added DoD section |
| `ADR-002-fastembed-mvp-embedding-layer.md` | Added DoD section |
| `ADR-003-mcp-python-sdk-mvp-agent-interface.md` | Added DoD section |
| `ADR-004-kuzu-rejected-mvp.md` | Added DoD section |
| `ADR-004-domain-model.md` | Added DoD section |
| `ADR-005-external-repos-reference-only.md` | Added DoD section |
| `ADR-006-tauri-mac-frontend-shell.md` | Added DoD section |

**Total: 7 ADR files updated**

## What Was Added

Each updated file received a **Definition of Done** section containing:

1. **Documentation Update Requirement** — Updates to README, setup commands, API docs, MCP docs, data models, etc.
2. **Comment Pass Requirement** — Plain-English comments for complex logic
3. **Peer Review Requirement** — Review report in `docs/quality/reviews/`, critical/high findings fixed or accepted
4. **Test Requirement** — Unit tests, integration tests, or documented manual validation
5. **ADR Update Requirement** — If architecture decisions changed
6. **Dependency Register Update Requirement** — If new packages were added
7. **External Code Boundary Check** — No imports from `external/reference/`
8. **Final Summary Requirement** — What changed, tests run, review result, docs updated, remaining risks, commands to run

## Why It Was Added

The OmniVia Constitution (Section 3.8) states: *"The specification is the source of truth. Code, prompts, UI and API behaviour must align to current specs."*

The existing `docs/quality/definition-of-done.md` already defined DoD criteria, but the individual spec, plan, and ADR files did not reference these requirements. Adding explicit DoD sections to each document:

- Ensures every spec, plan, and ADR has clear completion criteria
- Links back to the canonical DoD documentation
- Provides consistent guidance for future task completion
- Reinforces the external code boundary policy

## Specs Requiring Manual Review

The following files were **not** modified (intentionally excluded):

| File | Reason |
|------|--------|
| `specs/000-constitution/constitution.md` | Already contains DoD in Section 4 |
| `features/*/tasks.md` | Already contain basic DoD sections |
| `features/*/quickstart.md` | User-facing quick start, not implementation spec |
| `features/*/research.md` | Research notes, not implementation specs |
| `features/*/data-model.md` | Data model documentation, not implementation specs |
| `features/*/contracts/openapi.yaml` | API contract, not a spec document |
| `features/*/contracts/mcp-tools.json` | MCP tool definitions, not a spec document |
| `docs/adr/*` (updated) | All ADRs updated with DoD sections |

## Summary Statistics

| Category | Count |
|----------|-------|
| Spec specify.md files | 10 (all updated) |
| Spec plan.md files | 10 (all updated) |
| Feature spec.md files | 8 (4 existing, 4 updated) |
| Feature plan.md files | 10 (all updated) |
| ADR files | 7 (all updated) |
| **Total files updated** | **44** |

## Next Steps

1. Future tasks should reference the DoD sections when marking work complete
2. The `docs/quality/reviews/` directory should receive reports for each implementation task
3. Manual review of checkboxes in `specs/*/checklist.md` is still required (these are product fit checklists, not implementation completion checklists)