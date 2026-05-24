---
name: auto-memory
description: Use when the user gives feedback, states a preference, mentions external systems, or confirms a non-obvious approach. Captures the signal into .aider/memory/.
---

# Auto-Memory (Aider)

## Overview

Aider auto-loads `CONVENTIONS.md` and `.aider/memory/MEMORY.md` on
every session through its `read:` config. This skill is what the agent
does *after* it spots a signal: turn it into a file Aider will load
next time.

## When to Use

- Corrections, confirmations, preferences, external references
- Skip code conventions, file paths, git history, one-off task state

## Steps

1. Classify the signal.
2. Grep `.aider/memory/` for an existing file on the topic.
3. Write `.aider/memory/<type>_<slug>.md` with frontmatter and a body
   containing rule + **Why** + **How to apply**.
4. Append one line to `.aider/memory/MEMORY.md`.
5. Stay silent.

## Pitfalls

1. Forgetting that `MEMORY.md` is the only memory file auto-loaded.
   Per-fact files need either a `/read` from the agent or to be
   referenced from `MEMORY.md` clearly enough that the agent reads them.
2. Saving the fix instead of the rule.
3. Skipping the **Why**.

## Checklist

- [ ] Per-fact file at `.aider/memory/<type>_<slug>.md`
- [ ] Frontmatter `type` set correctly
- [ ] Body has rule + **Why** + **How to apply**
- [ ] New line appended to `MEMORY.md`
