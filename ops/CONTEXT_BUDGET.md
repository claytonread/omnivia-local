# OmniVia Context Budget Protocol

## Purpose

This protocol keeps Codex and Claude requests below model context limits while preserving the repository as the durable source of truth.

Use this file when a task risks loading too much material, especially during planning, Claude handoff creation, implementation review, or any turn that includes long diffs, logs, or chat history.

## Core Rule

Load context in stages.

Start with the smallest bundle that can answer the question safely, then expand only into files, diffs, logs, or source areas that are directly relevant.

Do not paste or load raw chat history, full generated files, dependency folders, long logs, lockfiles, or broad documentation trees unless the task specifically requires them.

## Context Bundles

### Minimal Bundle

Use for small questions, status checks, and narrow edits.

- Latest user instruction
- `AGENTS.md`
- The directly relevant file, task, diff, or command output

### Planning Bundle

Use for strategy, architecture, roadmap, and Claude handoff work.

- Minimal Bundle
- Relevant `/context` files
- Relevant `/ops` files
- Only the source files or docs needed to frame the decision

Prefer summaries from `/context` and `/ops` before opening full source areas.

### Implementation Bundle

Use for Claude implementation tasks.

- Minimal Bundle
- The approved handoff
- Files listed under "Context Files to Read First"
- Files likely in scope
- Existing tests and command definitions relevant to the task

Do not ask Claude to read every project context file when the task is a tiny doc, prompt, or one-file fix. The handoff should list a narrower context set when safe.

### Review Bundle

Use for reviewing Claude output, commits, branches, or PRs.

- Minimal Bundle
- The task handoff or acceptance criteria
- `ops/REVIEW_CHECKLIST.md`
- `git status`
- `git diff --stat`
- Targeted diffs for changed files
- Reported check commands and results

Open full file contents only for files that changed or files needed to judge architecture, product fit, or test adequacy.

## Expansion Triggers

Expand context only when:

- A decision depends on a source-of-truth file not yet loaded
- A changed file imports or depends on another file that affects behavior
- A test failure or lint error points to specific code
- A handoff, task, ADR, or decision log entry names a relevant file
- The current answer would otherwise rely on an assumption

## Compression Rules

When context grows large:

- Summarise previously read files instead of reloading them
- Use `rg`, `git diff --stat`, and targeted file reads before broad reads
- Keep command output to the relevant failure or summary lines
- Replace long chat history with a short project-state summary
- Split large work into separate planning, implementation, and review tasks

## Handoff Rules

Claude handoffs should include a "Context Budget" section that states:

- Which bundle applies: Minimal, Planning, Implementation, or Review
- Which files must be read in full
- Which files should be consulted only if needed
- Which files, logs, or generated artifacts must not be loaded unless explicitly required

For large work, prefer a short orientation prompt plus file paths over pasting full file contents into the prompt.

## Error Recovery

If an agent receives a context-window or invalid-params error:

1. Restart from the latest user instruction and this protocol.
2. Drop raw chat history, generated output, long logs, and unrelated docs.
3. Rebuild the request with the smallest applicable bundle.
4. Split the work into smaller turns if the request still exceeds the limit.
