# OmniVia Operating Model

## Purpose

This file defines how OmniVia is operated as an AI-assisted product project.

The operating model is designed around a clean split:

- Codex acts as project strategist, product architect, delivery orchestrator, and reviewer.
- Claude acts as programming and implementation agent.
- GitHub and the repository act as the durable source of truth.
- The user acts as founder, product owner, and final decision maker.

## Core Workflow

Use this loop for most work:

```text
Think -> Instruct -> Build -> Review -> Decide -> Commit or Merge
```

## Task Lanes

Use the smallest lane that protects the work.

### Tiny Lane

Use for one-file changes, documentation cleanup, prompt/template edits, or narrow follow-up fixes.

- Codex may provide a short instruction instead of a full handoff.
- Claude should use a single session.
- Run targeted checks only.
- No review reports required (unless user requests).
- Final response must still list changed files, checks run, and remaining risk.

### Standard Lane

Use for normal bounded implementation tasks with clear acceptance criteria.

- Codex should provide a bounded handoff with acceptance criteria.
- Claude should use `/goal` to drive implementation until acceptance criteria are satisfied.
- Claude may use subagents for test planning, review, docs drift, MCP contracts, or repo hygiene.
- Claude must run the exact required checks in the handoff.
- Claude must produce peer review and Definition of Done evidence.

### High-Risk Lane

Use for persistence, data model, MCP contracts, dependency changes, architecture changes, cross-module changes, or anything that could corrupt user/project data.

- Codex should provide a full handoff with explicit file boundaries and acceptance criteria.
- Claude should use `/goal` for multi-turn iteration toward acceptance criteria.
- Claude should use relevant subagents or an agent team where safe.
- Claude should stop for Codex/user direction if scope, product, architecture, or dependency decisions appear.
- Codex review is required before merge.
- Claude should not commit unless the handoff explicitly permits committing after all checks pass.

### 1. Think with Codex

Use Codex to clarify:

- What problem is being solved
- Why it matters
- Whether it fits the current roadmap
- What decisions are needed
- What implementation path is safest
- What should be deferred

### 2. Instruct Claude

Codex produces a precise Claude handoff.

Claude should receive a bounded task, not a vague project ambition.

### 3. Build with Claude

Claude implements the approved task.

Claude should:

- Inspect relevant repo files first
- Make the smallest coherent change
- Respect `AGENTS.md`
- Run relevant checks
- Commit only if explicitly permitted and DoD passes
- Report exact check commands and results; do not summarize a check as passing unless that exact command was run

For work that can be safely parallelised, Claude should use Claude Code agent teams. Agent teams are preferred for independent research, review, test planning and clearly separated implementation slices. They should not be used when multiple agents would edit the same files, when the task is small and sequential, or when a product/architecture decision is unresolved.

Project subagents live in `.claude/agents/` and should be used as specialist support inside Claude work:

- `omnivia-code-reviewer` checks implementation quality and DoD readiness
- `omnivia-test-planner` designs focused test coverage
- `omnivia-docs-guard` checks docs, ADRs, specs and task drift
- `omnivia-mcp-specialist` reviews MCP tool contracts and stdio behaviour
- `omnivia-repo-hygiene` checks git status, generated files and cleanup scope

When using an agent team, the Claude lead must:

- Define teammate responsibilities and file boundaries before implementation
- Keep shared context aligned to the Codex handoff
- Wait for teammates to complete before synthesising results
- Own final integration, tests, review reports and DoD
- Clean up the team after completion

### 4. Review with Codex

Codex reviews Claude output against:

- Product strategy
- Architecture notes
- Decision log
- Task acceptance criteria
- Build rules
- Git diff
- Definition of Done

### 5. Decide

The user decides whether to:

- Accept
- Amend
- Rework
- Revert
- Create follow-up tasks

## Default Commit Policy

Claude should not commit by default.

Claude may commit only when the handoff explicitly permits it and Definition of Done has passed.

For high-risk tasks, Claude should usually stop after implementation and checks so Codex can review before commit. If Claude has already committed and Codex finds issues, the preferred remedy is an amend commit within the same task scope, not a new unrelated cleanup task.

## Authority Boundaries

### Codex may decide or recommend

- Task sequencing
- Handoff quality
- Acceptance criteria
- Whether a task is too large
- Whether a change appears aligned or misaligned
- Whether a commit needs review before merge

### Codex should ask or escalate when

- Product positioning changes
- Major architecture changes are proposed
- Cloud-first assumptions are introduced
- Data model direction changes
- A dependency with long-term implications is introduced
- The task conflicts with the local-first strategy

### Claude may implement

- Code changes inside approved task scope
- Tests for approved behaviour
- Small refactors required by the task
- Build and lint fixes directly related to the task

### Claude should not independently decide

- Product positioning
- Major architecture
- Cloud migration direction
- New business workflow
- Data model redesign
- Broad dependency strategy
- Repo structure rewrite

## Repo as Source of Truth

OmniVia is currently operated by a solo founder/developer.

Git should be treated as the durable record for product code, product-facing documentation, and required runtime/build/test configuration. Local operating documents, Claude configuration, prompt templates, scratch planning, and other non-product Markdown do not need to be tracked in Git unless the user explicitly promotes them.

This is intentional. Do not repeatedly flag ignored non-product operating files as a problem merely because they are not tracked.

Track in Git:

- Product source code
- Required build and runtime configuration
- The `AGENTS.md` guidance file
- Curated context files in `/context` only if explicitly promoted
- Operating files in `/ops` only if explicitly promoted
- Product-facing documentation where useful

Keep local or ignored unless explicitly promoted:

- Raw ChatGPT or Claude exports
- General research dumps
- Temporary prompt scratchpads
- Local operating templates
- Local Claude configuration, subagents, commands, hooks, and runtime state
- Non-product planning Markdown
- Screenshots unless explicitly required
- Local cache or dependency folders
- Secrets or credentials

Promotion rule:

- Codex or Claude may recommend promoting a non-product file into Git only when there is a concrete reason, such as collaboration, reproducibility on another machine, CI enforcement, audit history, or product-facing documentation.
- Without that concrete reason, keep non-product Markdown and local agent operating files untracked.
- Do not change `.gitignore` for non-product files unless the user explicitly approves the policy change.

## Operating Files

### `/ops/ROADMAP.md`

Tracks strategic sequence and priority.

### `/ops/DECISION_LOG.md`

Records durable decisions and avoids re-litigating them.

### `/ops/TASK_BACKLOG.md`

Tracks implementation tasks, owner agent, status, acceptance criteria, and review state.

### `/ops/CLAUDE_HANDOFF_TEMPLATE.md`

Standard template for implementation prompts sent to Claude.

### `/ops/REVIEW_CHECKLIST.md`

Standard Codex checklist for reviewing Claude output.

### `/ops/REVIEW_WORKFLOW.md`

Complete review workflow with triggers, process steps, decision matrix, and examples.

### `/ops/WORKFLOW_PROMPTS.md`

Reusable prompts for planning, handoff generation, implementation review, and roadmap updates.

### `.claude/commands/`

Claude Code command files for automated workflows:

| Command | Purpose |
|---------|---------|
| `goal-implementation.md` | Goal-driven implementation with acceptance criteria tracking |
| `spec-drift-check.md` | Detect implementation/spec divergence |
| `dependency-audit.md` | Check for outdated Python dependencies |
| `finish-task.md` | Complete task completion protocol |
| `dod-check.md` | Verify Definition of Done |
| `peer-review.md` | Peer review checklist |
| `comment-pass.md` | Comment quality check |

### `.claude/hooks/`

Claude Code hooks for policy enforcement:

| Hook | Purpose |
|------|---------|
| `enforce_finish_task.py` | Block completion until DoD evidence exists |
| `pretool_block_dangerous.py` | Block dangerous git operations |
| `session_start_context.py` | Show context at session start |

## Planning Cadence

Use Codex to update `/ops` when:

- A new strategic decision is made
- A task is completed
- Claude output changes the implementation state
- The roadmap changes
- A risk becomes visible
- The repo structure changes

Do not turn `/ops` into a diary. Keep it concise, operational, and current.

`/ops` is the local operational source of truth for this solo workflow. It may remain ignored by Git. Only treat that as an issue if the user has explicitly asked for `/ops` content to be version-controlled or shared.

## Preferred Branch Workflow

Suggested branch pattern:

```text
main
feature/T-0001-local-vault-ingestion
feature/T-0002-file-inventory
fix/T-0003-path-handling
```

Preferred flow:

1. Codex prepares task and handoff
2. Claude works on a feature branch
3. Claude commits if DoD passes
4. Codex reviews branch or PR
5. User approves merge

## Manual First, Automate Later

Start with a manual handoff loop:

```text
User -> Codex -> Claude -> Codex review -> User approval
```

Agent teams are allowed inside the Claude implementation step where the handoff identifies safe parallel work. Broader automation beyond the Claude work session should wait until the manual Codex to Claude to Codex loop is reliable.

The first priority is clean authority boundaries, not automation.

## Claude Code Feature Integration

OmniVia leverages Claude Code's automation features to improve efficiency and quality.

### Goal-Driven Implementation (`/goal`)

Use `/goal` for tasks with clear, verifiable acceptance criteria.

- Run `/goal` with the acceptance criteria as the target condition
- A separate fast model judges criterion satisfaction after each turn
- Claude continues until the goal reports satisfaction
- Then run the finish protocol (comment pass, peer review, DoD check)

Example:
```bash
/goal all acceptance criteria from the handoff are satisfied
```

### Cloud Routines (`/schedule`)

Schedule recurring maintenance tasks to run independently:

| Routine | Frequency | Purpose |
|---------|-----------|---------|
| Spec drift check | Weekly | Verify implementation matches specs |
| Dependency audit | Weekly | Check for outdated/vulnerable deps |
| Task backlog review | Weekly | Groom open tasks, update statuses |
| Review report cleanup | Monthly | Archive old review reports |

Run `/schedule` to set up recurring prompts. Cloud routines run on Anthropic infrastructure and do not require an open Claude session.

### Claude Hooks

Hooks intercept Claude Code actions to enforce policies:

| Hook | When | Purpose |
|------|------|---------|
| `SessionStart` | Session begins | Show pending changes, open tasks, recent reviews |
| `PreToolUse` | Before tool call | Block dangerous operations (force push, hard reset) |
| `PostToolUse` | After tool call | Auto-format after edits (optional) |
| `Stop` | Task completes | Enforce Definition of Done |
| `TaskCompleted` | Task marked done | Enforce Definition of Done |

Hooks are configured in `.claude/settings.json`. Custom hook scripts live in `.claude/hooks/`.
