---
name: skill-distiller
description: Use when the user has issued the same multi-step instruction three or more times. Detects the moment and delegates authoring to the vendored skill-creator skill.
---

# Skill Distiller (Aider)

## Overview

Detection and authoring are different jobs. This skill owns detection.
Authoring is delegated to the vendored
[`skill-creator`](../skill-creator/SKILL.md) (Apache 2.0, from
Anthropic Skills).

When the trigger fires, `/read .aider/skills/skill-creator/SKILL.md`
in the Aider session so the agent loads its instructions, then ask it
to draft the new skill.

## When to Use

- A multi-step instruction has appeared in three separate sessions
- User asks "can you remember how I like to do X?"

## Steps

1. Confirm three repeats.
2. Pick a slug. Target path: `.aider/skills/<slug>/SKILL.md`.
3. `/read .aider/skills/skill-creator/SKILL.md` and then prompt:

   > Use the skill-creator instructions you just read to draft a new
   > skill at `.aider/skills/<slug>/SKILL.md`. Trigger description:
   > "Use when <one-line trigger>". Behaviour: <one-line summary>.

4. Show the draft to the user before committing.
5. Reference the new skill from `MEMORY.md` so the agent knows it exists.
6. Prune now-redundant feedback memories.

## Pitfalls

1. Distilling on the second occurrence.
2. Drafting the SKILL.md yourself instead of using skill-creator.
3. Forgetting that Aider needs `/read` to actually load skill-creator;
   the skill isn't auto-loaded.

## Checklist

- [ ] Three or more repeats confirmed
- [ ] skill-creator loaded via `/read` before drafting
- [ ] Draft approved by user
- [ ] New skill referenced from `MEMORY.md`
- [ ] Superseded memories pruned
