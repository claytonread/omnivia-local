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

The repository should contain:

- Product source code
- Required build and runtime configuration
- The `AGENTS.md` guidance file
- Curated context files in `/context`
- Operating files in `/ops`
- Product-facing documentation where useful

The repository should not contain:

- Raw ChatGPT or Claude exports
- General research dumps
- Temporary prompt scratchpads
- Screenshots unless explicitly required
- Local cache or dependency folders
- Secrets or credentials

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

## Planning Cadence

Use Codex to update `/ops` when:

- A new strategic decision is made
- A task is completed
- Claude output changes the implementation state
- The roadmap changes
- A risk becomes visible
- The repo structure changes

Do not turn `/ops` into a diary. Keep it concise, operational, and current.

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

Only automate Claude execution or multi-agent orchestration after the manual loop is reliable.

The first priority is clean authority boundaries, not automation.
