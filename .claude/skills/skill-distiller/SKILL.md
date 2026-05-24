---
name: skill-distiller
description: Use when the user has issued the same multi-step instruction three or more times across sessions. Distills the repeated workflow into a new SKILL.md so the agent stops needing to be re-taught.
version: 1.0.0
author: self-learning-agent
license: MIT
---

# Skill Distiller

## Overview

Memory captures *facts*. Skills capture *workflows*. When the user finds
themselves typing the same multi-step recipe a third time — "first run
the linter, then the type-checker, then commit with this format" — it's
time to lift it out of conversation and into a reusable skill.

## When to Use

- The same instruction sequence has appeared in ≥3 separate turns
- The user explicitly asks: *"can you remember how I like to do X?"*
- You catch yourself re-deriving the same plan from memory snippets

**Do not use for:** one-off tasks, anything covered by an existing skill
(extend it instead), or workflows so trivial they fit in one memory line.

## Steps

1. **Survey peers** in `.claude/skills/` — match tone and structure.
2. **Pick a slug**: lowercase, hyphens, ≤ 64 chars, verb-led
   (`deploy-staging`, `triage-flaky-test`).
3. **Write** `.claude/skills/<slug>/SKILL.md` with this shape:

   ```yaml
   ---
   name: <slug>
   description: Use when <trigger>. <one-line behavior>.
   version: 1.0.0
   ---
   ```

   Body sections: **Overview → When to Use → Steps → Pitfalls → Verification Checklist.**
4. **Cross-link** related skills and memories with plain markdown links.
5. **Propose, don't impose** — show the draft to the user before committing.
   Skills are durable; a bad skill silently warps every future session.

## Pitfalls

1. **Distilling too early.** Two occurrences is coincidence. Three is a
   pattern. Wait for three.
2. **Skill descriptions that don't start with "Use when…".** The
   description is the trigger — write it so future-you can decide
   relevance in one read.
3. **One skill per micro-step.** Bundle the whole recipe. Ten tiny skills
   that always fire together should be one skill.
4. **Forgetting to delete the now-redundant memories.** Once a workflow
   is a skill, the feedback memories that taught it are noise. Remove
   them and their `MEMORY.md` entries.

## Verification Checklist

- [ ] Trigger appeared ≥ 3 times across sessions
- [ ] No existing skill already covers it
- [ ] Frontmatter starts at byte 0; `description` starts with "Use when"
- [ ] Body has Overview, When to Use, Steps, Pitfalls, Checklist
- [ ] Superseded memory entries have been pruned
