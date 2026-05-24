---
name: auto-memory
description: Use when the user gives feedback, states a preference, mentions external systems, or confirms a non-obvious approach. Captures the signal into .claude/memory/ so it survives across sessions.
version: 1.0.0
author: self-learning-agent
license: MIT
---

# Auto-Memory

## Overview

A self-learning agent is only as good as what it *keeps*. This skill is the
write-side of the memory loop: turn fleeting user signal into a durable
file under `.claude/memory/`, then index it in `MEMORY.md`.

## When to Use

- User corrects your approach: `"no, don't…"`, `"stop doing X"`, `"never…"`
- User confirms a non-obvious approach: `"yes exactly"`, `"perfect, keep doing that"`
- User reveals their role, expertise, or working style
- User mentions an external system (Linear board, Grafana dashboard, Slack channel)
- User states a deadline, ongoing initiative, or stakeholder constraint

**Do not use for:** code conventions visible in the repo, file paths,
git history facts, or one-off task state. Those belong in the code or in
your current task list, not in memory.

## Steps

1. **Classify the signal** as one of: `user`, `feedback`, `project`, `reference`.
2. **Check for duplicates** — grep `.claude/memory/` for the topic first.
   If an existing memory covers it, *update* that file instead of creating
   a new one.
3. **Write the memory file** at `.claude/memory/<type>_<slug>.md`:

   ```markdown
   ---
   name: <slug>
   description: <one-line summary used to judge relevance later>
   metadata:
     type: <user|feedback|project|reference>
   ---

   <Rule or fact in one sentence.>

   **Why:** <reason the user gave — often a past incident>
   **How to apply:** <when this guidance should fire>
   ```

4. **Append to MEMORY.md** — one line:
   `- [<Title>](<filename>.md) — <one-line hook>`
5. **Stay silent about it.** Don't announce the save. The user will notice
   you stopped repeating the mistake.

## Pitfalls

1. **Saving the *fix* instead of the *rule*.** "We changed line 42" is
   git's job. "Never mock the DB in integration tests — prior incident
   masked a broken migration" is memory's job.
2. **Skipping the Why.** Without the reason, future-you can't judge edge
   cases and will either over- or under-apply the rule.
3. **Duplicate memories.** Two files saying the same thing means neither
   gets updated when the rule changes. Grep first.
4. **Memorizing the codebase.** File paths, function names, architecture —
   read the code, don't cache it. It rots.
5. **Announcing saves.** "I've remembered that!" turns a quiet trust loop
   into a chatty one. Just do it.

## Verification Checklist

- [ ] File lives at `.claude/memory/<type>_<slug>.md`
- [ ] Frontmatter starts at byte 0 with `---`
- [ ] `type` is one of user/feedback/project/reference
- [ ] Body has a one-line rule plus **Why** and **How to apply**
- [ ] A new line was added to `MEMORY.md`
- [ ] No duplicate of an existing memory
