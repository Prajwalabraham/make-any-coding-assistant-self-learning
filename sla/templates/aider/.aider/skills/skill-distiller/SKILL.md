---
name: skill-distiller
description: Use when the user has issued the same multi-step instruction three or more times. Distills the workflow into a new SKILL.md.
---

# Skill Distiller (Aider)

## Overview

When a multi-step recipe repeats a third time, lift it out of conversation
into `.aider/skills/<name>/SKILL.md`.

## When to Use

- A multi-step instruction has appeared in three separate sessions
- User asks "can you remember how I like to do X?"

## Steps

1. Survey peer skills in `.aider/skills/`.
2. Pick a verb-led slug.
3. Write `.aider/skills/<slug>/SKILL.md` with standard frontmatter and
   the five-section body.
4. Reference the new skill from `MEMORY.md` so the agent knows it exists.
5. Show the draft to the user before committing.

## Pitfalls

1. Distilling on the second occurrence.
2. Descriptions that don't start with "Use when...".
3. One skill per micro-step.

## Checklist

- [ ] Trigger appeared three or more times
- [ ] `description` starts with "Use when"
- [ ] Body has all five sections
- [ ] Skill referenced from `MEMORY.md`
