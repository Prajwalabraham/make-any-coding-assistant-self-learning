# How to Make Claude Code (or Any Coding Agent) Self-Learn

*Stop teaching the same lesson twice. A plug-and-play `.claude/` setup,
inspired by the Hermes Agent.*

> **TL;DR** — A self-learning agent is just three flat files and a hook.
> Persona (`SOUL.md`), memory (`MEMORY.md` + small per-fact files), and
> skills (`SKILL.md` per workflow). Add one `UserPromptSubmit` hook that
> nudges the model to *save* on every signal, and one `SessionStart`
> hook that *reloads* what it saved last time. Clone the repo, drop the
> folder into any project, you're done.
>
> Repo layout and installers are in this README. The article is ~7 min.

---

## The problem nobody talks about

Every coding agent — Claude Code, Codex, Cursor, Cline, you name it — ships
with the same amnesia. You spend an hour Tuesday explaining that your team
never mocks the database in integration tests because of that one prod
migration that blew up last quarter. The agent nods, fixes the test, you
ship. Wednesday morning, new session, fresh agent. It writes a mock.

You re-type the explanation. Wednesday afternoon, different file. It
writes another mock.

You either:
1. Give up and just review every diff carefully forever, or
2. Stuff a 4,000-line `CLAUDE.md` with every preference you've ever had,
   which the model then half-ignores because no human (or model) reads
   4,000 lines carefully on every turn.

There's a third option. Make the agent **learn** instead of **read**.

---

## What I learned from tearing apart Hermes

Before writing this, I dug into the [Hermes Agent](https://hermes.dev)
install on my own machine — `%LOCALAPPDATA%\hermes\`. Hermes is one of
the more interesting open-source CLI agents around because it treats
"learning" as a first-class architectural concern, not a CLAUDE.md
dumping ground.

Stripped to its essence, Hermes has four artifacts:

```
~/.hermes/
├── SOUL.md              # persona — reloaded every message
├── memories/
│   ├── MEMORY.md        # cross-context facts (azure config, etc.)
│   └── USER.md          # user-specific preferences
├── skills/
│   └── <category>/<name>/SKILL.md   # ~80 skills, each one workflow
└── hooks/               # shell hooks that fire on events
```

That's it. No vector DB. No fine-tuning. No graph of embeddings. Just
**markdown the agent reads on every turn and writes to when it learns
something.**

The trick is the *discipline* around what goes where:

- **SOUL.md** = how I talk. Tone, defaults, the "way of working." Empty
  by default; the user shapes it.
- **MEMORY.md / USER.md** = facts I shouldn't have to ask again. Hermes'
  own MEMORY.md on my machine is two lines — *"uses Azure Foundry with
  this endpoint"* and *"Steam lives at C:\Program Files (x86)\Steam,
  permitted to clean CS2 crash dumps."* Tiny. Load-bearing.
- **SKILL.md** = recipes. Every skill is a markdown file with frontmatter
  (`name`, `description starting with "Use when..."`) and a body
  (Overview → When to Use → Steps → Pitfalls → Checklist). When a
  workflow stabilizes, it gets distilled into a skill so the agent
  stops re-deriving it.

This is the entire blueprint. Everything below is "how do we port this
to Claude Code (or any agent) and make the *agent itself* maintain it
over time."

---

## The three-layer model

Think of agent learning the same way you think of human learning:

| Layer | Human equivalent | Files | When to write |
|-------|------------------|-------|---------------|
| **Persona** | Your personality | `SOUL.md` | When the user corrects your *style* |
| **Memory** | Episodic recall | `memory/*.md` | When the user gives a *fact* or *preference* |
| **Skills** | Muscle memory | `skills/<name>/SKILL.md` | When a *workflow* repeats 3+ times |

The bug in most CLAUDE.md-based setups is that all three layers get
crammed into one file. Then the model has to do classification *and*
retrieval *and* application on every turn, with no structure to help
it. Splitting them lets each layer evolve at its own pace — your
persona barely changes, your memory grows weekly, your skill set grows
monthly.

---

## Factor 1 — Capture signal, don't capture transcripts

The most common mistake I see in "memory" plugins is dumping the entire
conversation into a log and calling it learning. That's not memory.
That's tape.

**Signal** is the small subset of user turns that contain a durable
rule. Three patterns matter:

1. **Corrections** — "no", "don't", "stop", "never", "that's wrong"
2. **Confirmations** — "yes, exactly", "perfect", "keep doing that"
3. **Preferences** — "I prefer", "from now on", "in this repo we"
4. **References** — "check the Linear board", "the Grafana dashboard at"

Corrections are obvious. Confirmations are the underrated half — if you
only save corrections, the agent learns to be timid; saving confirmations
teaches it which judgment calls *worked*.

The repo in this article ships a `UserPromptSubmit` hook
(`.claude/hooks/capture_signal.py`) that detects these cues and nudges
the model — "hey, this looks like signal, consider invoking the
`auto-memory` skill before you reply." The model still decides what to
save. The hook just makes sure it *considers* saving every time.

```python
# .claude/hooks/capture_signal.py  (excerpt)
CORRECTION   = re.compile(r"\b(no,?\s|don't|stop|never|wrong)\b", re.I)
CONFIRMATION = re.compile(r"\b(yes,?\s+exactly|perfect|keep doing)\b", re.I)
PREFERENCE   = re.compile(r"\b(i prefer|from now on|in this (repo|project))\b", re.I)
```

Heuristic regex is good enough. The model does the real work.

---

## Factor 2 — One fact per file, plus an index

Hermes' MEMORY.md is a flat append-only log. That works for a personal
assistant with 20 facts. It breaks at 200.

A better pattern, borrowed from how my own Claude Code memory system
is wired:

```
.claude/memory/
├── MEMORY.md                    # one-line index, always loaded
├── user_role.md                 # one fact per file
├── feedback_no_db_mocks.md
├── project_q2_migration.md
└── reference_linear_ingest.md
```

`MEMORY.md` is the *only* file always in context. It looks like:

```markdown
- [User role](user_role.md) — senior backend, deep Go, new to React
- [No DB mocks](feedback_no_db_mocks.md) — integration tests hit real PG
- [Q2 migration](project_q2_migration.md) — auth rewrite, legal-driven
- [Linear INGEST](reference_linear_ingest.md) — pipeline bug tracker
```

The model loads MEMORY.md every session, scans for relevance, and
*selectively* reads the per-fact files when one applies. That's the same
trick humans use: an index of "things I know" plus the ability to recall
the detail when needed.

Each fact file follows a tiny schema:

```markdown
---
name: no-db-mocks
description: integration tests must hit a real database
metadata:
  type: feedback
---

Integration tests must hit a real PostgreSQL, never mocks.

**Why:** Q3 2025 incident — mocked tests passed but the prod migration
failed because the mock didn't enforce a CHECK constraint.
**How to apply:** When writing or reviewing anything under `tests/integration/`.
```

The **Why** is the load-bearing field. Without it, future-you can't
judge edge cases and the rule decays into either over-application
("never mock anything ever") or quiet drift ("did we really mean it?").

---

## Factor 3 — Skills are workflows, memory is facts

A common failure mode: people try to store "how to deploy to staging"
as a memory. It works for a while. Then the deploy gets complicated, the
memory turns into a 40-line wall of bullet points, and the model starts
ignoring it because it's longer than everything else in the index.

That's not memory. That's a **skill**. Different artifact, different
lifecycle.

Promote to a skill when:

- A workflow has been re-instructed 3+ times across sessions
- It has actual *steps* (not just a fact)
- It has pitfalls worth documenting

The repo's `skill-distiller` skill encodes this rule:

> Two occurrences is coincidence. Three is a pattern. Wait for three.

Skill files live in `.claude/skills/<name>/SKILL.md` and follow Hermes'
exact shape:

```markdown
---
name: deploy-staging
description: Use when the user asks to deploy to staging or push a release candidate. Runs lint → typecheck → tag → push in that order.
---

# Deploy Staging

## Overview
...

## When to Use
- "deploy staging", "ship to staging", "cut a release candidate"

## Steps
1. ...

## Pitfalls
...

## Verification Checklist
- [ ] ...
```

The `description` field is the **trigger** — write it so the model can
decide relevance from a 30-character skim of the skill index. Start with
"Use when…" and you're 90% there.

---

## Factor 4 — Hooks turn "good intentions" into "guaranteed behavior"

You can write the best CLAUDE.md in the world telling the agent to
"please remember to save corrections." It will forget half the time
because nothing forces it to *consider* the question.

Hooks fix this. Claude Code (and most modern CLI agents) ship two
event types that matter for self-learning:

| Hook | Fires when | What it does for learning |
|------|-----------|---------------------------|
| `SessionStart` | New session opens | Loads SOUL.md + MEMORY.md + skill list into context |
| `UserPromptSubmit` | Each user message | Scans for signal, nudges model to save if found |

The repo ships both as ~50-line Python scripts. They don't *do* the
saving — the model does. They just **make sure the model considers it.**
That's the difference between "the agent might learn" and "the agent
will learn."

```json
// .claude/settings.json (excerpt)
{
  "hooks": {
    "SessionStart": [{ "matcher": "*", "hooks": [
      { "type": "command", "command": "python .claude/hooks/session_start.py" }
    ]}],
    "UserPromptSubmit": [{ "matcher": "*", "hooks": [
      { "type": "command", "command": "python .claude/hooks/capture_signal.py" }
    ]}]
  }
}
```

---

## Factor 5 — A librarian agent to keep it clean

Memory rots. A fact you saved in March about "the auth service runs on
port 8080" becomes a lie in June when the team moves it to 8443.

The repo includes a `memory-keeper` subagent (`.claude/agents/memory-keeper.md`)
whose only job is curation:

- Read every memory file
- Check it against the current codebase
- Delete contradicted facts, merge overlaps, archive unused entries
- Rebuild MEMORY.md as a clean index

Run it weekly, or whenever MEMORY.md crosses ~150 lines. It's the same
pattern as `git gc` — your memory store needs maintenance the same way
your repo does.

---

## Factor 6 — Silence is the feature

The single most important UX rule: **don't announce what you learned.**

Every "I've remembered that you prefer X!" message turns the trust loop
into a chatty one and trains the user to ignore your output. The right
behavior is invisible: the user notices, three weeks later, that you
*stopped* writing DB mocks. That's the win condition.

The persona file in this repo enforces it explicitly:

> *"When the user corrects you, update the relevant memory file before
> continuing. Do not announce the save."*

---

## What it looks like in practice

Week 1, fresh install. The agent works like a stock Claude Code session.
You correct it twice about something. Both corrections get saved to
`feedback_*.md` files. MEMORY.md grows by two lines.

Week 2. New session, different file. The SessionStart hook loads MEMORY.md.
The agent sees the rule, applies it silently, never writes the mock.

Week 4. You've explained your release process three times. The `skill-distiller`
fires, drafts a `deploy-staging` skill, shows it to you. You tweak one
line, save. Now every future "deploy staging" request runs the recipe
without re-instruction.

Week 8. You run the `memory-keeper` agent. It archives 11 outdated facts
from when you were still on the old auth service. MEMORY.md slims back
down to ~40 lines of high-signal entries.

The agent is now genuinely *better* in your repo than a fresh install
would be — not because the model changed, but because the **scaffolding
around it** captured the months of context you'd otherwise have to
re-explain.

---

## Repo layout

```
.
├── README.md             # this article
├── install.ps1           # Windows installer
├── install.sh            # macOS / Linux installer
├── LICENSE
└── .claude/
    ├── CLAUDE.md         # the learning protocol the agent reads on every turn
    ├── SOUL.md           # persona — empty-ish by default
    ├── settings.json     # registers the two hooks
    ├── memory/
    │   └── MEMORY.md     # the index (starts empty)
    ├── skills/
    │   ├── auto-memory/SKILL.md       # write-side: capture signal
    │   └── skill-distiller/SKILL.md   # write-side: distill repeated workflows
    ├── agents/
    │   └── memory-keeper.md           # weekly curation subagent
    └── hooks/
        ├── session_start.py    # loads SOUL + MEMORY + skill list each session
        └── capture_signal.py   # detects correction/confirmation/preference cues
```

## Install

**Windows (PowerShell):**

```powershell
git clone https://github.com/<your-fork>/make-any-coding-assistant-self-learning
cd make-any-coding-assistant-self-learning
.\install.ps1 -Target C:\path\to\your\project
```

**macOS / Linux:**

```bash
git clone https://github.com/<your-fork>/make-any-coding-assistant-self-learning
cd make-any-coding-assistant-self-learning
./install.sh /path/to/your/project
```

Then open the target project in Claude Code. The `SessionStart` hook
fires immediately, bootstraps the agent with the (empty) memory store,
and you're learning from turn one.

## Porting to Codex, Cursor, Cline, Aider

The pattern is hook-agnostic. The four pieces — persona file, memory
index, skill folder, signal-capture hook — work in any agent that:

1. Loads a project-local config file at session start, AND
2. Lets you inject context before the model responds

For **Cursor:** put `CLAUDE.md` contents into `.cursor/rules`; replace
the hook with a `.cursorrules` injection.
For **Codex CLI:** use `AGENTS.md` instead of `CLAUDE.md`; Codex
respects the same memory-file pattern if you reference it from
`AGENTS.md`.
For **Aider:** put the bootstrap context into a `CONVENTIONS.md` and
include it on every run with `aider --read CONVENTIONS.md`.

The artifacts are markdown. They're portable on purpose.

---

## The point

Every hour you spend re-explaining the same thing to your coding agent
is an hour the agent could have spent *being useful in your codebase
specifically.* The gap between "stock Claude Code" and "Claude Code that
knows your project as well as a six-month engineer" is not a smarter
model. It's a hundred small markdown files that capture what you've
already told it.

Build the scaffolding once. Let the agent maintain it. Stop teaching the
same lesson twice.

---

*Want to contribute a skill or an agent? PRs welcome. The repo is MIT.
If you fork it, share what your agent learned — the best skills come
from real workflows, not toy examples.*
