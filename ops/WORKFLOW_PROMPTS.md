# OmniVia Workflow Prompts

## 1. Codex Repo Inspection Prompt

```text
Read AGENTS.md and /ops/CONTEXT_BUDGET.md first.
Then read only the relevant /context and /ops files needed for repo inspection.
Then inspect the current repository structure and summarise the implementation state.
Do not modify files.

Report:
1. Detected framework and runtime
2. Package manager
3. Build, dev, lint, and test commands
4. App and package structure
5. Current source folders
6. Current gaps or unknowns
7. Best next 3 implementation tasks
8. Any risks before using Claude for implementation
```

## 2. Codex Strategy Prompt

```text
Read AGENTS.md and /ops/CONTEXT_BUDGET.md first.
Then read the relevant /context and /ops files needed for this decision.
I want to make a product or architecture decision for OmniVia.

Frame the decision clearly.
Provide:
1. Decision to make
2. Recommendation
3. Alternatives
4. Trade-offs
5. Risks
6. What should be logged in /ops/DECISION_LOG.md
7. Whether this should produce a Claude implementation handoff

Do not write code.
```

## 3. Codex Claude Handoff Prompt

```text
Read AGENTS.md and /ops/CONTEXT_BUDGET.md first.
Then read only the relevant /context and /ops files needed to create this handoff.
Create a Claude-ready implementation handoff for the next task.
Use /ops/CLAUDE_HANDOFF_TEMPLATE.md.

The handoff must include:
- Task ID
- Goal
- Business reason
- Task lane: Tiny, Standard, or High-risk
- Context budget: Minimal, Planning, Implementation, or Review
- Context files to read first
- Files to consult only if needed
- Files, logs, or generated artifacts not to load unless explicitly required
- Repo inspection instructions
- Files likely in scope
- Files out of scope
- Agent mode: Single session, Subagents only, or Agent team
- Agent team guidance: safe teammate boundaries and file ownership if applicable
- Relevant OmniVia subagents to use, such as `omnivia-code-reviewer`, `omnivia-test-planner`, `omnivia-docs-guard`, `omnivia-mcp-specialist` or `omnivia-repo-hygiene`
- Step-by-step instructions
- Acceptance criteria
- Exact required check commands
- Required quality evidence table
- Definition of Done
- Git instructions
- Required final response format

Do not implement the task yourself.
```

## 4. Claude Implementation Prompt Wrapper

```text
You are the implementation agent for OmniVia.
Read AGENTS.md, /ops/CONTEXT_BUDGET.md, and the task handoff below before changing files.

Follow the handoff exactly.
Respect the handoff's Context Budget section. Load only the files needed for the task and avoid raw chat history, generated files, broad documentation trees, and long logs unless explicitly required.
Do not make major product or architecture decisions.
If the task requires a major decision, stop and report the decision needed.
Make the smallest coherent change.
Run relevant checks.
Report exact check commands and results.
Commit only if the handoff explicitly allows committing and Definition of Done passes.

[PASTE HANDOFF HERE]
```

## 4a. Claude Agent Team Prompt Wrapper

Use this wrapper only when the task handoff says an agent team is appropriate.

```text
You are the lead implementation agent for OmniVia.
Read AGENTS.md, CLAUDE.md, /ops/CONTEXT_BUDGET.md and the task handoff below before changing files.

Respect the handoff's Context Budget section. Load only the files needed for the task and avoid raw chat history, generated files, broad documentation trees, and long logs unless explicitly required.

Use Claude Code agent teams where the work can be safely parallelised.

Before spawning teammates:
1. Identify independent work streams.
2. Assign clear file boundaries.
3. Keep teammates out of the same files unless one teammate is read-only.
4. Use teammate plan approval for risky work.
5. Stop and ask for Codex/user direction if a product or architecture decision is needed.

Use the OmniVia project subagents where relevant:
- `omnivia-code-reviewer` for post-change review
- `omnivia-test-planner` for coverage planning
- `omnivia-docs-guard` for docs/spec/ADR/task drift checks
- `omnivia-mcp-specialist` for MCP tool and stdio server work
- `omnivia-repo-hygiene` before final status or commit

The lead agent remains responsible for:
- final integration
- tests and checks
- peer review and DoD reports
- generated-file cleanup
- final completion summary

Do not make major product or architecture decisions.
If the task requires a major decision, stop and report the decision needed.
Commit only if the handoff explicitly allows committing and Definition of Done passes.

[PASTE HANDOFF HERE]
```

## 5. Codex Review Prompt

```text
Read AGENTS.md and /ops/CONTEXT_BUDGET.md first.
Then read the task-relevant /context and /ops files, including /ops/REVIEW_CHECKLIST.md.
Review the latest Claude output, git diff, branch, commit, or PR.

Start with git status and git diff --stat, then inspect targeted diffs and changed files only as needed.

Check against:
- Task acceptance criteria
- Definition of Done
- Architecture notes
- Product direction
- Repo hygiene
- Build, lint, and test evidence
- Whether reported check commands match the required scope
- Whether Agent Mode and subagent guidance were followed

Report:
1. Recommendation: Accept, Accept with follow-up tasks, Amend, Rework, Revert, or Blocked
2. Summary
3. What looks good
4. Issues found
5. Required changes
6. Suggested follow-up tasks
7. Merge readiness
```

## 6. Backlog Update Prompt

```text
Read AGENTS.md and /ops/CONTEXT_BUDGET.md first.
Then read the relevant /context and /ops files needed for the backlog update.
Update /ops/TASK_BACKLOG.md based on the latest completed work, review findings, and roadmap direction.

Rules:
- Keep tasks small and implementation-ready where possible
- Add acceptance criteria
- Mark completed tasks Done only when accepted
- Do not add speculative tasks unless they support the current roadmap
- Keep the backlog concise
```

## 7. Decision Log Update Prompt

```text
Read AGENTS.md and /ops/CONTEXT_BUDGET.md first.
Then read the relevant /context and /ops files needed for the decision.
Update /ops/DECISION_LOG.md for the latest decision.

Use the existing decision format.
Include:
- Status
- Date
- Owner
- Decision
- Rationale
- Consequences
- Review trigger

Do not rewrite unrelated decisions.
```
