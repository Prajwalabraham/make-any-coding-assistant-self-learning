# How to Make Claude Code (or Any Coding Agent) Self-Learn

*A plug-and-play `.claude/` setup that turns feedback, preferences, and repeated workflows into durable agent memory. Inspired by the Hermes Agent.*

> **TL;DR.** A self-learning agent is just three flat files and a hook. Persona (`SOUL.md`), memory (`MEMORY.md` plus small per-fact files), and skills (one `SKILL.md` per workflow). Add a `UserPromptSubmit` hook that nudges the model to save on every signal, and a `SessionStart` hook that reloads what it saved last time. Schedule the cleanup. Clone the repo, drop the folder into any project, you're done.
>
> Repo layout and installers are below. The article is about a 7 minute read.

---

## The problem nobody talks about

Every coding agent ships with the same amnesia. Claude Code, Codex, Cursor, Cline, all of them. You spend twenty minutes Tuesday morning explaining that your team uses pnpm, that commits follow Conventional Commits, that nothing gets force-pushed to `main`. The agent nods, fixes the bug, you ship. Wednesday morning, new session, fresh agent. It runs `npm install`, writes a commit message like "fixed stuff", and tries to `git push --force` when the rebase conflicts.

You re-type the explanation. Wednesday afternoon, different file, same drift.

You either give up and review every diff carefully forever, or you stuff a 4,000 line `CLAUDE.md` with every preference you've ever had. The model then half-ignores it, because no human (or model) reads 4,000 lines carefully on every turn.

There's a third option. Make the agent *learn* instead of *read*.

---

## What I learned from tearing apart Hermes

Before writing this I dug into the [Hermes Agent](https://hermes.dev) install on my own machine, the one sitting at `%LOCALAPPDATA%\hermes\`. Hermes is interesting because it treats "learning" as a first-class architectural concern rather than a CLAUDE.md dumping ground.

Stripped to its essence, Hermes has four artifacts:

```
~/.hermes/
├── SOUL.md              # persona, reloaded every message
├── memories/
│   ├── MEMORY.md        # cross-context facts
│   └── USER.md          # user-specific preferences
├── skills/
│   └── <category>/<name>/SKILL.md   # ~80 skills, each one workflow
└── hooks/               # shell hooks that fire on events
```

That's it. No vector database. No fine-tuning. No graph of embeddings. Just markdown that the agent reads on every turn and writes to whenever it learns something.

The trick is the discipline around what goes where.

- `SOUL.md` is how I talk. Tone, defaults, the way of working. Empty by default; the user shapes it.
- `MEMORY.md` and `USER.md` are facts I shouldn't have to ask again. Things like "we use pnpm, not npm", "the staging URL is staging.acme.dev", "all PRs need at least one reviewer from the platform team". Tiny entries. Load-bearing.
- `SKILL.md` files are recipes. Each one has frontmatter (a `name` and a `description` starting with "Use when…") and a body with five sections: Overview, When to Use, Steps, Pitfalls, Checklist. When a workflow stabilizes, it gets distilled into a skill so the agent stops re-deriving it every time.

That is the entire blueprint. Everything below is how to port it to Claude Code (or any other agent) and have the *agent itself* maintain it over time.

---

## The three-layer model

Think of agent learning the same way you think of human learning.

| Layer | Human equivalent | Files | When to write |
|-------|------------------|-------|---------------|
| Persona | Your personality | `SOUL.md` | When the user corrects your *style* |
| Memory | Episodic recall | `memory/*.md` | When the user gives a *fact* or *preference* |
| Skills | Muscle memory | `skills/<name>/SKILL.md` | When a *workflow* repeats three or more times |

The bug in most CLAUDE.md-based setups is that all three layers get crammed into one file. The model then has to do classification, retrieval, and application on every turn, with no structure to help it. Splitting them lets each layer evolve at its own pace. Your persona barely changes. Your memory grows weekly. Your skill set grows monthly.

---

## Factor 1. Capture signal, don't capture transcripts

The most common mistake in "memory" plugins is dumping the entire conversation into a log and calling it learning. That isn't memory. That's tape.

Signal is the small subset of user turns that contain a durable rule. Four patterns matter.

1. **Corrections.** "No", "don't", "stop", "never", "that's wrong".
2. **Confirmations.** "Yes, exactly", "perfect", "keep doing that".
3. **Preferences.** "I prefer", "from now on", "in this repo we".
4. **References.** "Check the Linear board", "the Grafana dashboard at…".

Corrections are obvious. Confirmations are the underrated half. If you only save corrections the agent learns to be timid; saving confirmations teaches it which judgment calls actually worked.

The repo ships a `UserPromptSubmit` hook (`.claude/hooks/capture_signal.py`) that detects these cues and nudges the model. *"This looks like signal, consider invoking the `auto-memory` skill before you reply."* The model still decides what to save. The hook just makes sure it considers saving every time.

```python
# .claude/hooks/capture_signal.py  (excerpt)
CORRECTION   = re.compile(r"\b(no,?\s|don't|stop|never|wrong)\b", re.I)
CONFIRMATION = re.compile(r"\b(yes,?\s+exactly|perfect|keep doing)\b", re.I)
PREFERENCE   = re.compile(r"\b(i prefer|from now on|in this (repo|project))\b", re.I)
```

Heuristic regex is good enough. The model does the real work.

---

## Factor 2. One fact per file, plus an index

Hermes' MEMORY.md is a flat append-only log. That works for a personal assistant with twenty facts. It breaks at two hundred.

A better pattern looks like this:

```
.claude/memory/
├── MEMORY.md                          # one-line index, always loaded
├── user_role.md                       # one fact per file
├── feedback_research_before_plan.md
├── feedback_git_discipline.md
├── project_q2_payments_refactor.md
└── reference_linear_pay_board.md
```

`MEMORY.md` is the only file always in context. It looks like:

```markdown
- [User role](user_role.md) — senior backend engineer, ten years Go, new to React
- [Research before planning](feedback_research_before_plan.md) — read the code first, then propose
- [Git discipline](feedback_git_discipline.md) — never force-push to shared branches
- [Q2 payments refactor](project_q2_payments_refactor.md) — Stripe → Adyen migration, ships Aug
- [Linear PAY board](reference_linear_pay_board.md) — payments bugs tracked here
```

The model loads `MEMORY.md` every session, scans for relevance, and selectively reads the per-fact files when one applies. Same trick humans use. An index of "things I know", plus the ability to recall the detail when needed.

Each fact file follows a tiny schema:

```markdown
---
name: research-before-plan
description: always read the relevant code before proposing a plan
metadata:
  type: feedback
---

Before proposing a plan or refactor, read the files that would actually
change. No plans drafted from filenames alone.

**Why:** Agent proposed a "simple" auth refactor based on grep results,
missed that the middleware was already half-rewritten on a feature
branch, and the plan was wrong from step one.
**How to apply:** Any request that starts with "plan", "design",
"refactor", "how should we". Read the surface area first, then plan.
```

The `Why` is the load-bearing field. Without it future-you can't judge edge cases, and the rule decays into either over-application ("never propose anything without reading the whole repo") or quiet drift ("did we really mean it?").

---

## Factor 3. Skills are workflows, memory is facts

A common failure mode: people try to store "how to cut a release" as a memory. It works for a while. Then the release process gets complicated, the memory turns into a forty line wall of bullet points, and the model starts ignoring it because it's longer than everything else in the index.

That isn't memory. That's a skill. Different artifact, different lifecycle.

Promote a memory to a skill when:

- A workflow has been re-instructed three or more times across sessions.
- It has actual steps, not just a fact.
- It has pitfalls worth documenting.

The repo's `skill-distiller` skill encodes the rule plainly:

> Two occurrences is coincidence. Three is a pattern. Wait for three.

Skill files live at `.claude/skills/<name>/SKILL.md` and follow Hermes' exact shape:

```markdown
---
name: cut-release
description: Use when the user asks to cut a release, tag a version, or publish a new build. Runs the changelog, version bump, tag, and CI trigger in order.
---

# Cut Release

## Overview
Standard release flow for this repo. Use it instead of doing the steps by hand.

## When to Use
- "cut a release", "tag v...", "publish a new build", "ship a version"

## Steps
1. ...

## Pitfalls
...

## Verification Checklist
- [ ] ...
```

The `description` field is the trigger. Write it so the model can decide relevance from a thirty character skim of the skill index. Start with "Use when…" and you're ninety percent there.

---

## Factor 4. Hooks turn "good intentions" into "guaranteed behavior"

You can write the best CLAUDE.md in the world telling the agent to "please remember to save corrections". It will forget half the time, because nothing forces it to consider the question.

Hooks fix this. Claude Code (and most modern CLI agents) ship two event types that matter for self-learning.

| Hook | Fires when | What it does for learning |
|------|-----------|---------------------------|
| `SessionStart` | A new session opens | Loads SOUL.md, MEMORY.md, and the skill list into context |
| `UserPromptSubmit` | Each user message | Scans for signal, nudges the model to save if found |

The repo ships both as fifty-line Python scripts. They don't *do* the saving. The model does. They just make sure the model considers it. That's the difference between "the agent might learn" and "the agent will learn".

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

## Factor 5. Let the agent do its own garbage collection, on a cron

Memory rots. A fact you saved in March about "the auth service runs on port 8080" becomes a lie in June when the team moves it to 8443. If you have to remember to clean it up manually, you won't.

Good news: modern coding agents already support scheduled execution. Claude Code has a `/schedule` slash command (and a `CronCreate` tool under the hood) that runs an agent on a cron. Cursor has background agents that can be triggered on a schedule via its API. Codex CLI is scriptable; pair it with the OS cron or a GitHub Action and you have the same thing. There is no reason for the librarian to be a manual chore.

The repo ships a `memory-keeper` subagent (`.claude/agents/memory-keeper.md`) whose only job is curation. Read every memory file, check each against the current codebase, delete contradicted facts, merge overlapping ones, archive entries that haven't been referenced in a quarter, rebuild `MEMORY.md` as a clean index.

To wire it up, run this once inside your project (Claude Code):

```
/schedule create
  name: memory-keeper-weekly
  cron: 0 9 * * 1
  prompt: Run the memory-keeper subagent. Report a one-line summary
          of kept, merged, archived, deleted.
```

That runs every Monday at 9am. You see a summary in your notifications, the memory store stays tight, and you never have to think about it. Same pattern works on any agent that supports scheduled execution; the prompt is identical, only the scheduling command changes.

Think of it as `git gc` for your agent's brain.

---

## Factor 6. Silence is the feature

The single most important UX rule: *don't announce what you learned.*

Every "I've remembered that you prefer X!" message turns the trust loop into a chatty one and trains the user to ignore your output. The right behavior is invisible. The user notices, three weeks later, that you *stopped* writing commits like "fixed stuff". That is the win condition.

The persona file in this repo enforces it explicitly:

> *"When the user corrects you, update the relevant memory file before continuing. Do not announce the save."*

---

## What it looks like in practice

Week one, fresh install. The agent works like a stock Claude Code session. You correct it twice about something. Both corrections get saved to `feedback_*.md` files. `MEMORY.md` grows by two lines.

Week two. New session, different file. The `SessionStart` hook loads `MEMORY.md`. The agent sees the rule, applies it silently, never makes the same mistake.

Week four. You've explained your release process three times. The `skill-distiller` fires, drafts a `cut-release` skill, shows it to you. You tweak one line, save. Every future "cut a release" request now runs the recipe without re-instruction.

Week eight. The Monday 9am cron fires `memory-keeper`. It archives eleven outdated facts from when you were still on the old auth service. `MEMORY.md` slims back down to forty lines of high-signal entries. You see a one-line notification, nothing more.

The agent is now genuinely better in your repo than a fresh install would be. Not because the model changed, but because the scaffolding around it captured the months of context you'd otherwise have to re-explain.

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
    ├── SOUL.md           # persona, mostly empty by default
    ├── settings.json     # registers the two hooks
    ├── memory/
    │   └── MEMORY.md     # the index (starts empty)
    ├── skills/
    │   ├── auto-memory/SKILL.md       # write-side: capture signal
    │   └── skill-distiller/SKILL.md   # write-side: distill repeated workflows
    ├── agents/
    │   └── memory-keeper.md           # curation subagent, run via /schedule
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

Open the target project in Claude Code. The `SessionStart` hook fires immediately, bootstraps the agent with the (empty) memory store, and you're learning from turn one. Schedule the memory-keeper with `/schedule create` once and forget it.

## Porting to Codex, Cursor, Cline, Aider

The pattern is hook-agnostic. The four pieces (persona file, memory index, skill folder, signal-capture hook) work in any agent that loads a project-local config file at session start and lets you inject context before the model responds.

For **Cursor**, put `CLAUDE.md` contents into `.cursor/rules` and replace the hook with a `.cursorrules` injection. For **Codex CLI**, use `AGENTS.md` instead of `CLAUDE.md`; Codex respects the same memory-file pattern if you reference it from `AGENTS.md`. For **Aider**, put the bootstrap context into a `CONVENTIONS.md` and include it on every run with `aider --read CONVENTIONS.md`.

The artifacts are markdown. They're portable on purpose.

---

## The point

Every hour you spend re-explaining the same thing to your coding agent is an hour the agent could have spent being useful in your codebase specifically. The gap between "stock Claude Code" and "Claude Code that knows your project as well as a six-month engineer" isn't a smarter model. It's a hundred small markdown files that capture what you've already told it.

Build the scaffolding once. Let the agent maintain it. Stop teaching the same lesson twice.

---

*Want to contribute a skill or an agent? PRs welcome. The repo is MIT. If you fork it, share what your agent learned. The best skills come from real workflows, not toy examples.*
