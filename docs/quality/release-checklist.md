# OmniVia Release Checklist

Use this before tagging a local MVP release or major working slice.

## Product

- [ ] Product behaviour matches the current specs.
- [ ] No accidental SMB OS scope has entered OmniVia.
- [ ] Local-first principle remains intact.

## Runtime

- [ ] Local runtime starts from documented commands.
- [ ] Data persists across restart.
- [ ] Required Docker services start.
- [ ] Environment variables are documented.

## Memory and Agent Safety

- [ ] Agent-created memories default to proposed.
- [ ] Approved/rejected/superseded status behaviour works.
- [ ] Agent requests are logged.
- [ ] Restricted content is handled safely.

## Source and Retrieval

- [ ] Sources are referenced where relevant.
- [ ] Search results are traceable.
- [ ] Re-ingestion does not duplicate unchanged records.

## Quality

- [ ] Tests pass.
- [ ] Peer review report exists.
- [ ] Critical/High review findings are resolved.
- [ ] Comment pass has been completed.

## Documentation

- [ ] README is current.
- [ ] Setup instructions are current.
- [ ] API/MCP docs are current.
- [ ] Specs and tasks are current.
- [ ] ADRs are current.
- [ ] Dependency register is current.
