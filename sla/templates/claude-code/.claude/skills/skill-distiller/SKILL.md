---
name: skill-distiller
description: Use when the user has issued the same multi-step instruction three or more times across sessions, or when the `[self-learning]` signal hook reports a correction pattern that has fired 3+ times. Detects the moment, then delegates the actual skill authoring to the vendored `skill-creator` skill.
version: 1.1.0
author: self-learning-agent
license: MIT
---

# Skill Distiller

## Overview

This skill is a *trigger*, not an *author*. Detection and authoring are
two different jobs; keeping them separate lets the self-learning loop
own the "when to promote" decision while Anthropic's official
[`skill-creator`](../skill-creator/SKILL.md) skill owns the "how to
write a good SKILL.md, eval it, optimise its description" part.

When you decide to promote a workflow, do not draft the new SKILL.md
yourself. Invoke `skill-creator` and let it run its full authoring
flow: draft, test prompts, evals, description optimisation.

## When to Use

- A multi-step instruction has appeared in three separate sessions
- The `capture_signal.py` hook has emitted "Pattern has repeated 3+
  times" for a correction cue
- The user explicitly asks "can you remember how I like to do X?"
- You catch yourself re-deriving the same plan from memory snippets

## Steps

1. **Confirm the trigger.** Three is the floor, not the ceiling. Two
   occurrences is coincidence. If unsure, count back through memory
   entries on the same topic.
2. **Pick a slug and a target path.** Verb-led, lowercase, hyphens.
   For Claude Code the path is `.claude/skills/<slug>/SKILL.md`.
3. **Hand off to skill-creator.** State the intent in one paragraph
   and invoke the [`skill-creator`](../skill-creator/SKILL.md) skill:

   > Use the skill-creator skill to draft a new skill at
   > `.claude/skills/<slug>/SKILL.md`. Trigger description: "Use when
   > <one-line trigger>". Behaviour: <one-line summary>. Follow the
   > full skill-creator flow including the description optimiser
   > (`scripts/improve_description.py`) so the trigger matches reliably.

4. **Show the draft to the user before committing.** Skill-creator's
   default mode is conversational; let the user evaluate the draft and
   any test prompts. Do not save until the user approves.
5. **Prune.** Once the skill exists, remove the now-redundant feedback
   memory entries that captured the workflow piecemeal, and delete
   their lines from `MEMORY.md`.

## Pitfalls

1. **Distilling on the second occurrence.** Wait for three.
2. **Drafting the SKILL.md yourself instead of using skill-creator.**
   You'll miss the description optimiser and the eval loop, both of
   which materially improve trigger reliability. Use the tool that
   exists.
3. **One skill per micro-step.** Bundle related steps into one skill.
4. **Forgetting to prune the now-redundant memories.** Duplicated
   guidance in two places (memory and skill) drifts apart.

## Verification Checklist

- [ ] Trigger appeared three or more times across sessions
- [ ] No existing skill covers it
- [ ] `skill-creator` was invoked for authoring, not bypassed
- [ ] Description was run through `improve_description.py`
- [ ] Draft was shown to the user before commit
- [ ] Superseded memory entries pruned from `MEMORY.md`
