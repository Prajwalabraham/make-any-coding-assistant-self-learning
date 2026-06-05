# How to Make Claude Code (or Any Coding Agent) Self-Learn

*A plug-and-play scaffold that turns feedback, preferences, and repeated workflows into durable agent memory. One-line install, real adapters for Claude Code, Codex, Cursor, and Aider. Inspired by the Hermes Agent.*

> **TL;DR.** A self-learning agent is just three flat files and a trigger. Persona, memory index, and skills, plus a way to make the model *consider* saving on every turn. The architecture is the same across agents; the wiring is different. This repo ships real adapters for all four major coding-agent CLIs and a one-line installer that picks the right one.
>
> ```bash
> curl -fsSL https://raw.githubusercontent.com/Prajwalabraham/make-any-coding-assistant-self-learning/main/install.sh | bash
> ```
>
> Article is about a 7 minute read.

---

## The problem nobody talks about

Every coding agent ships with the same amnesia. Claude Code, Codex, Cursor, Cline, all of them. You spend twenty minutes Tuesday morning explaining that your team uses pnpm, that commits follow Conventional Commits, that nothing gets force-pushed to `main`. The agent nods, fixes the bug, you ship. Wednesday morning, new session, fresh agent. It runs `npm install`, writes a commit message like "fixed stuff", and tries to `git push --force` when the rebase conflicts.

You re-type the explanation. Wednesday afternoon, different file, same drift.

You either give up and review every diff carefully forever, or you stuff a 4,000 line `CLAUDE.md` (or `AGENTS.md`, or `.cursorrules`) with every preference you've ever had. The model then half-ignores it, because no human (or model) reads 4,000 lines carefully on every turn.

There's a third option. Make the agent *learn* instead of *read*.

---

## Why this exists (and why not just use Hermes, OpenClaw, or OpenCode)

The honest version: frameworks like [Hermes](https://hermes.dev), [OpenClaw](https://openclaw.ai/), and [OpenCode](https://github.com/sst/opencode) already have excellent self-learning architectures. Persona files, memory stores, skill libraries, hooks, the works. If you're starting fresh, install one of those and move on.

The catch is that almost nobody reading this is starting fresh.

If you've spent the last six months getting productive in Claude Code (or Cursor, or Codex), switching is a tax most devs won't pay. You'd be giving up the IDE integration you actually use. You'd be re-learning a new TUI, a new keybinding set, a new failure-mode catalogue. You'd be standing up the environment from zero, authoring every skill and agent before any of it is useful. And whether the alternative is a general-purpose personal assistant (Hermes, OpenClaw) or a from-scratch OSS coding agent (OpenCode), the same problem applies: they're built for the developer who picks their tool today, not the one who picked it last year and has muscle memory in it now.

So most devs don't migrate. They stay in their current agent, keep re-typing the same instructions every session, and the self-learning idea stays a curiosity rather than something they actually get to use.

This repo is the wedge. **It takes the architectural ideas from Hermes and its cousins (persona, memory, skills, scheduled cleanup) and ports them as a plug-and-play scaffold into the agents devs already use.** No migration. No new UI. No abandoning your existing setup. One curl-bash, pick your agent, keep working. The architecture is what matters; the tool you run it in shouldn't have to change.

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

That is the entire blueprint. Everything below is how to port it to *your* agent (Claude Code, Codex, Cursor, or Aider) without pretending the wiring is identical across all four. It isn't.

---

## The three-layer model (and why it's portable)

The *concept* is portable across agents. The *files* are not.

| Layer | Human equivalent | What it is | When to write |
|-------|------------------|------------|---------------|
| Persona | Your personality | Tone, defaults, way of working | When the user corrects your *style* |
| Memory | Episodic recall | One file per fact, plus an always-loaded index | When the user gives a *fact* or *preference* |
| Skills | Muscle memory | One file per workflow, loaded on demand | When a *workflow* repeats three or more times |

The bug in most CLAUDE.md-based setups is that all three layers get crammed into one file. The model then has to do classification, retrieval, and application on every turn, with no structure to help it. Splitting them lets each layer evolve at its own pace.

Where it gets agent-specific is the wiring:

| Agent | Persona/protocol file | Memory location | Auto-load mechanism | Trigger mechanism |
|-------|----------------------|-----------------|---------------------|-------------------|
| Claude Code | `.claude/CLAUDE.md` + `SOUL.md` | `.claude/memory/` | `SessionStart` hook | `UserPromptSubmit` hook |
| Codex CLI | `AGENTS.md` | `.agents/memory/` | Codex auto-reads `AGENTS.md` | Model self-prompts (no shell hooks) |
| Cursor | `.cursor/rules/00-self-learning-protocol.mdc` | `.cursor/memory/` mirrored into `10-memory-index.mdc` | `alwaysApply: true` rules | Rules-as-context |
| Aider | `CONVENTIONS.md` (via `.aider.conf.yml`) | `.aider/memory/` | `read:` list in config | Model self-prompts |

Only Claude Code has a real shell-level hook system. Codex and Aider lean on the model self-prompting from instructions in the auto-loaded file. Cursor has no hooks but has a powerful always-applied rules system that does the same job. **The repo ships actual templates for each shape**, not a one-size-fits-all that you have to adapt.

---

## Factor 1. Capture signal, don't capture transcripts

The most common mistake in "memory" plugins is dumping the entire conversation into a log and calling it learning. That isn't memory. That's tape.

Signal is the small subset of user turns that contain a durable rule. Four patterns matter.

1. **Corrections.** "No", "don't", "stop", "never", "that's wrong".
2. **Confirmations.** "Yes, exactly", "perfect", "keep doing that".
3. **Preferences.** "I prefer", "from now on", "in this repo we".
4. **References.** "Check the Linear board", "the Grafana dashboard at…".

Corrections are obvious. Confirmations are the underrated half. If you only save corrections the agent learns to be timid; saving confirmations teaches it which judgment calls actually worked.

On Claude Code this is enforced with a `UserPromptSubmit` hook that pattern-matches incoming prompts and nudges the model with `additionalContext`. On Codex and Aider there's no shell hook, so the equivalent lives inside the protocol file itself: an explicit instruction in `AGENTS.md` / `CONVENTIONS.md` telling the model to consider saving on every turn. On Cursor, the protocol rule has `alwaysApply: true` so the same instruction lands in every context window.

Different mechanisms, same outcome. The model is forced to *consider* saving every time.

---

## Factor 2. One fact per file, plus an index

Hermes' MEMORY.md is a flat append-only log. That works for a personal assistant with twenty facts. It breaks at two hundred.

A better pattern looks like this:

```
memory/
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

The model loads `MEMORY.md` every session, scans for relevance, and selectively reads the per-fact files when one applies. Same trick humans use. An index of things you know, plus the ability to recall the detail when needed.

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

The `Why` is the load-bearing field. Without it future-you can't judge edge cases, and the rule decays into either over-application or quiet drift.

---

## Factor 3. Skills are workflows, memory is facts

A common failure mode: people try to store "how to cut a release" as a memory. It works for a while. Then the release process gets complicated, the memory turns into a forty line wall of bullet points, and the model starts ignoring it.

That isn't memory. That's a skill. Different artifact, different lifecycle.

Promote a memory to a skill when:

- A workflow has been re-instructed three or more times across sessions.
- It has actual steps, not just a fact.
- It has pitfalls worth documenting.

Each agent has its own skills location:

- **Claude Code:** `.claude/skills/<name>/SKILL.md`
- **Codex:** `.agents/skills/<name>/SKILL.md`
- **Cursor:** `.cursor/rules/skills/<slug>.mdc` (with `alwaysApply: false`, loaded by description match)
- **Aider:** `.aider/skills/<name>/SKILL.md`

The `description` field is the trigger. Write it so the model can decide relevance from a thirty character skim. Start with "Use when…" and you're ninety percent there.

The repo's `skill-distiller` skill encodes the promotion rule plainly:

> Two occurrences is coincidence. Three is a pattern. Wait for three.

**Authoring is delegated to Anthropic's official [skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator)** (Apache 2.0), vendored under each agent's skills directory. Detection and authoring are different jobs: the self-learning loop decides *when* to promote a workflow; skill-creator handles *how* to draft a good SKILL.md, run evaluations, and tune the description for reliable triggering. The wrapper skill (`skill-distiller`) is intentionally thin and hands off as soon as the three-repeat threshold trips. Cursor's template references the upstream methodology by URL instead of vendoring, since its rules use `.mdc` rather than `SKILL.md`.

---

## Factor 4. Make consideration mandatory, not optional

You can write the best `CLAUDE.md` / `AGENTS.md` in the world telling the agent to "please remember to save corrections". It will forget half the time because nothing forces it to consider the question.

The agents that ship real hook systems get this for free. Claude Code has `SessionStart` and `UserPromptSubmit` hooks (this repo ships both as fifty-line Python scripts). They don't *do* the saving. The model does. They just make sure the model considers it.

```json
// .claude/settings.json (Claude Code only)
{
  "hooks": {
    "SessionStart": [{ "matcher": "*", "hooks": [
      { "type": "command", "command": "python3 .claude/hooks/session_start.py" }
    ]}],
    "UserPromptSubmit": [{ "matcher": "*", "hooks": [
      { "type": "command", "command": "python3 .claude/hooks/capture_signal.py" }
    ]}]
  }
}
```

The other three agents (Codex, Cursor, Aider) don't have shell hooks. The fallback is to put the "consider saving on every turn" instruction inside the auto-loaded protocol file itself, then rely on the model's instruction-following. It's less reliable than a hook, but with a clear instruction repeated every session, it works most of the time. (Cursor's always-applied rules system makes it about as reliable as Claude's hooks; Codex and Aider are looser.)

---

## Factor 5. Let the agent do its own garbage collection, on a cron

Memory rots. A fact you saved in March about "the auth service runs on port 8080" becomes a lie in June when the team moves it to 8443. If you have to remember to clean it up manually, you won't.

Good news: modern coding agents already support scheduled execution.

- **Claude Code:** built-in `/schedule` slash command. `/schedule create memory-keeper-weekly '0 9 * * 1'` and you're done.
- **Cursor:** Background Agents support cron schedules via the dashboard. Point one at the keeper prompt.
- **Codex / Aider:** no built-in scheduler. Run via OS cron, Task Scheduler, or a weekly GitHub Action that calls `codex exec --file ...` / `aider --message-file ...`.

The repo ships a `memory-keeper` prompt for each agent, in its agent-native location. Its only job is curation. Read every memory file, check each against the current codebase, delete contradicted facts, merge overlapping ones, archive entries that haven't been referenced in a quarter, rebuild `MEMORY.md` as a clean index.

Think of it as `git gc` for your agent's brain. Wire it once, forget it.

---

## Factor 6. Silence is the feature

The single most important UX rule: *don't announce what you learned.*

Every "I've remembered that you prefer X!" message turns the trust loop into a chatty one and trains the user to ignore your output. The right behavior is invisible. The user notices, three weeks later, that you *stopped* writing commits like "fixed stuff". That is the win condition.

Every persona template in this repo enforces it explicitly:

> *"When the user corrects you, update the relevant memory file before continuing. Do not announce the save."*

---

## What it looks like in practice

Week one, fresh install. The agent works like a stock session. You correct it twice about something. Both corrections get saved to `feedback_*.md` files. `MEMORY.md` grows by two lines.

Week two. New session, different file. The protocol fires (via hook on Claude Code, via always-loaded rule on Cursor, via auto-read `AGENTS.md`/`CONVENTIONS.md` on Codex/Aider). The agent sees the rule, applies it silently, never makes the same mistake.

Week four. You've explained your release process three times. The `skill-distiller` fires, drafts a `cut-release` skill, shows it to you. You tweak one line, save. Every future "cut a release" request now runs the recipe without re-instruction.

Week eight. The Monday 9am cron fires `memory-keeper`. It archives eleven outdated facts from when you were still on the old auth service. `MEMORY.md` slims back down to forty lines of high-signal entries.

The agent is now genuinely better in your repo than a fresh install would be. Not because the model changed, but because the scaffolding around it captured the months of context you'd otherwise have to re-explain.

---

## Install

One line on macOS / Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/Prajwalabraham/make-any-coding-assistant-self-learning/main/install.sh | bash
```

One line on Windows (PowerShell):

```powershell
iwr -useb https://raw.githubusercontent.com/Prajwalabraham/make-any-coding-assistant-self-learning/main/install.ps1 | iex
```

The bootstrap downloads the repo, drops a `sla` binary onto your PATH, and immediately runs an interactive prompt:

```
sla init  self-learning scaffold for coding agents

  Which coding agent?
    1) Claude Code
    2) Codex CLI
    3) Cursor
    4) Aider
  > 1

  Install scope?
    1) this project (cwd)
    2) global (your home config)
  > 1

  ==> installing claude-code into /Users/you/code/your-repo
  Proceed? [Y/n] y
  + wrote .claude/CLAUDE.md
  + wrote .claude/SOUL.md
  + wrote .claude/settings.json
  ...
  + self-learning agent installed.

  next: open the project in Claude Code. The SessionStart hook
        bootstraps the agent on first turn. Schedule the keeper
        with: /schedule create memory-keeper-weekly '0 9 * * 1'
```

It refuses to overwrite existing files without an explicit `y`, so it's safe to run over an existing project. Re-run `sla init` any time to add a different agent (the four don't conflict; you can run `claude` and `codex` against the same repo).

---

## Repo layout

```
.
├── README.md                  # this article
├── install.sh / install.ps1   # curl-bash bootstraps
├── sla/
│   ├── sla                    # bash CLI (interactive onboarding)
│   ├── sla.ps1                # PowerShell CLI
│   └── templates/
│       ├── claude-code/.claude/...     # hooks, settings.json, skills, agents, memory
│       ├── codex/AGENTS.md + .agents/...
│       ├── cursor/.cursor/{rules,memory,agents}/...
│       └── aider/CONVENTIONS.md + .aider.conf.yml + .aider/...
└── LICENSE
```

Each template directory is a faithful expression of that agent's real config shape. No portability hand-waving; if you open `sla/templates/cursor/` you get actual `.mdc` rule files with `alwaysApply`/`description` frontmatter, not Claude Code files renamed.

## Contributing

PRs welcome. The two highest-leverage contributions are:

1. **A new agent template.** If you're a Cline / Continue / Roo / Aider-fork user, add `sla/templates/<agent>/` matching that tool's real config layout.
2. **A real skill.** If you've found a workflow that distills cleanly into a `SKILL.md`, drop it in the relevant template's `skills/`. The best skills come from real workflows, not toy examples.

---

## The point

Every hour you spend re-explaining the same thing to your coding agent is an hour the agent could have spent being useful in your codebase specifically. The gap between "stock agent" and "agent that knows your project as well as a six-month engineer" isn't a smarter model. It's a hundred small markdown files that capture what you've already told it.

Install the scaffolding once. Let the agent maintain it. Stop teaching the same lesson twice.
