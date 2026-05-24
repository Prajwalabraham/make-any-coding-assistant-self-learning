---
name: skill-distiller
description: Use when the user has issued the same multi-step instruction three or more times across sessions. Distills the repeated workflow into a new SKILL.md.
---

# Skill Distiller (Codex)

## Overview

Memory captures facts. Skills capture workflows. When the user repeats
a multi-step recipe a third time, lift it out of conversation and into
a reusable skill at `.agents/skills/<name>/SKILL.md`.

## When to Use

- A multi-step instruction has appeared in three separate sessions
- The user asks: "can you remember how I like to do X?"
- You catch yourself re-deriving the same plan from memory snippets

## Steps

1. Survey peer skills in `.agents/skills/`.
2. Pick a verb-led slug, lowercase, hyphens.
3. Write `.agents/skills/<slug>/SKILL.md` with the standard frontmatter
   and the five sections: Overview, When to Use, Steps, Pitfalls,
   Checklist.
4. Cross-link related skills and memories with markdown links.
5. Show the draft to the user before committing.

## Pitfalls

1. Distilling on the second occurrence. Wait for three.
2. Descriptions that don't start with "Use when...". The description is
   the trigger.
3. One skill per micro-step. Bundle related steps into one skill.
4. Forgetting to delete the now-redundant memories.

## Checklist

- [ ] Trigger appeared three or more times
- [ ] No existing skill covers it
- [ ] Frontmatter `description` starts with "Use when"
- [ ] Body has all five sections
- [ ] Superseded memory entries removed from MEMORY.md
