# OmniVia Claude Open Source Review Setup

This pack contains the files you need to make Claude inspect, review and decide how OmniVia should use the open source repositories.

## What This Does

It sets up:

- `CLAUDE.md` project instructions
- Claude custom slash commands
- external repo folders
- open source review templates
- dependency register
- setup scripts
- a clear runbook

## Where to Put These Files

Copy the contents of this folder into the root of your OmniVia project.

Your project should then look roughly like this:

```text
omnivia-project/
  CLAUDE.md
  .claude/
    commands/
      review-oss.md
      review-oss-all.md
      consolidate-oss.md
      update-speckit-from-oss.md
  external/
    reference/
    sidecars/
    vendor/
  docs/
    open-source/
  scripts/
    setup-external-repos.sh
    make-external-dirs.sh
  .gitignore.append
```

## Fast Setup

From your OmniVia project root:

```bash
chmod +x scripts/make-external-dirs.sh
chmod +x scripts/setup-external-repos.sh

./scripts/make-external-dirs.sh
./scripts/setup-external-repos.sh
```

Then add the gitignore rules:

```bash
cat .gitignore.append >> .gitignore
```

Then open Claude Code from the project root:

```bash
claude
```

Inside Claude Code, run:

```text
/review-oss-all
```

After that completes, run:

```text
/consolidate-oss
```

Then run:

```text
/update-speckit-from-oss
```

## Recommended Review Order

The all-in-one command will follow this order:

1. EngramMemory
2. MarkItDown
3. Unstructured
4. GraphRAG
5. Graphiti
6. Cognee
7. Kuzu

## Important Rule

Claude should review and recommend first.

It should not copy external repo code into OmniVia source folders unless you explicitly approve it and the licence register says it is allowed.
