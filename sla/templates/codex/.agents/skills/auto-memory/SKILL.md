---
name: auto-memory
description: Use when the user gives feedback, states a preference, mentions external systems, or confirms a non-obvious approach. Captures the signal into .agents/memory/ so it survives across sessions.
---

# Auto-Memory (Codex)

## Overview

Turn fleeting user signal into a durable file under `.agents/memory/`,
then index it in `MEMORY.md`. Codex has no native hook system, so the
"trigger" is the model itself, prompted by `AGENTS.md` to consider
saving on every turn.

## When to Use

- User correction: "no", "don't", "stop", "never"
- User confirmation: "yes exactly", "perfect", "keep doing that"
- Preference: "I prefer", "from now on", "in this repo"
- External reference: Linear, Jira, Grafana, Slack channel, runbook URL

Do not use for code conventions visible in the repo, file paths, git
history, or one-off task state.

## Steps

1. Classify: `user`, `feedback`, `project`, or `reference`.
2. Grep `.agents/memory/` for an existing file on the topic. Update if
   found.
3. Write `.agents/memory/<type>_<slug>.md` with frontmatter and a body
   containing the rule, a **Why**, and a **How to apply**.
4. Append one line to `.agents/memory/MEMORY.md`.
5. Stay silent. Do not announce the save.

## Pitfalls

1. Saving the fix instead of the rule. Git remembers the fix; memory
   remembers the rule.
2. Skipping the **Why**. Without it, the rule decays.
3. Duplicate files. Grep first.
4. Caching the codebase. File paths and function names rot; read the
   code instead.

## Checklist

- [ ] File at `.agents/memory/<type>_<slug>.md`
- [ ] Frontmatter `type` is one of user/feedback/project/reference
- [ ] Body has rule + **Why** + **How to apply**
- [ ] New line appended to `MEMORY.md`
