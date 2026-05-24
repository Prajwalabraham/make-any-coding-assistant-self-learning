---
name: skill-distiller
description: Use when the user has issued the same multi-step instruction three or more times across sessions. Detects the moment and delegates the actual skill authoring to the vendored skill-creator skill.
---

# Skill Distiller (Codex)

## Overview

Detection and authoring are different jobs. This skill owns detection:
"the user has now repeated this recipe three times, it's time to
promote it to a skill." Authoring is delegated to the vendored
[`skill-creator`](../skill-creator/SKILL.md) (Apache 2.0, from
Anthropic Skills), which knows how to draft, eval, and tune the
description for reliable triggering.

## When to Use

- A multi-step instruction has appeared in three separate sessions
- The user explicitly asks "can you remember how I like to do X?"
- You catch yourself re-deriving the same plan from memory snippets

## Steps

1. Confirm three repeats. Two is coincidence.
2. Pick a slug. Target path: `.agents/skills/<slug>/SKILL.md`.
3. Hand off:

   > Use the skill-creator skill to draft a new skill at
   > `.agents/skills/<slug>/SKILL.md`. Trigger description: "Use when
   > <one-line trigger>". Behaviour: <one-line summary>. Follow the
   > full skill-creator flow including the description optimiser.

4. Show the draft to the user before committing.
5. Prune now-redundant feedback memories from `MEMORY.md`.

## Pitfalls

1. Distilling on the second occurrence.
2. Drafting the SKILL.md yourself instead of using skill-creator.
3. One skill per micro-step.
4. Forgetting to prune.

## Checklist

- [ ] Three or more repeats confirmed
- [ ] `skill-creator` invoked, not bypassed
- [ ] Draft approved by user
- [ ] Superseded memories pruned
