---
name: memory-init
description: Use ONLY when the user explicitly asks to initialize, bootstrap, seed, or backfill the memory base from past Claude sessions (e.g. "/memory-init", "build my memory from history", "seed memory from old chats"). Mines local or global session transcripts into durable memory files. Do NOT trigger on ordinary corrections or preferences — those go through auto-memory.
version: 1.0.0
author: self-learning-agent
license: MIT
---

# Memory-Init

## Overview

`auto-memory` captures signal going *forward*, one turn at a time. This skill
seeds the store from everything that happened *before* it was installed: it
reads your past Claude Code session transcripts, distills the durable signal,
and writes it into `.claude/memory/` in the exact format `auto-memory` uses.

The mechanical work — locating transcripts, parsing JSONL, stripping tool and
command noise, deduping — is done by a **read-only** Python extractor. It never
writes anything. Every memory file is written here, in the main loop, only
after you approve the proposed list. Re-running is safe and incremental.

## When to Use

- The user just installed the self-learning scaffold and wants memory seeded
  from prior work, not from scratch.
- The user says: "initialize memory", "bootstrap from my history", "seed memory
  from past sessions", "backfill memory", or invokes `/memory-init`.

**Do not use for:** a single in-conversation correction or preference — that is
`auto-memory`'s job. This skill is a deliberate, bulk bootstrap.

## Inputs

| Source | Where |
|--------|-------|
| Transcript store | `~/.claude/projects/<encoded-cwd>/<session>.jsonl` (default) |
| Extractor | `.claude/skills/memory-init/scripts/extract_candidates.py` |
| Existing memory | `.claude/memory/*.md` + `MEMORY.md` |
| Run manifest | `.claude/memory/.init_manifest.json` (tracks processed sessions) |

## Steps

1. **Choose scope.** Ask the user once: **local** (only sessions whose `cwd`
   matches this project) or **global** (every project under the store). Do not
   assume — local pulls focused, project-relevant facts; global is a full sweep
   that may surface facts from unrelated repos.

2. **Run the extractor** (read-only) with the chosen scope. Pass the manifest
   so already-processed sessions are skipped:

   ```bash
   python3 .claude/skills/memory-init/scripts/extract_candidates.py \
     --scope <local|global> \
     --project-root "<absolute path to this project>" \
     --manifest .claude/memory/.init_manifest.json
   ```

   It prints a JSON digest to stdout: `candidates` (each with `text`,
   `suggested_type`, `cues`, `project`, `timestamp`, `fingerprint`),
   plus `scanned_sessions` and counts. If it returns
   `{"error": "store_not_found"}`, tell the user no transcripts exist yet and
   stop.

3. **Classify and condense.** For each candidate, decide its real
   `user | feedback | project | reference` type — `suggested_type` is a hint
   from a regex, not gospel. Rewrite the raw snippet into a single durable
   sentence plus **Why** / **How to apply** (feedback/project) following the
   `auto-memory` contract. Discard candidates that are ephemeral task chatter,
   not a lasting rule. Merge candidates that say the same thing.

4. **Dedupe against existing memory.** Read `.claude/memory/*.md` and
   `MEMORY.md`. If a distilled fact already exists, drop it or fold the new
   nuance into the existing file — never create a second file for one fact.

5. **Review gate.** Present the final proposed list to the user as one table:
   `type | slug | one-line hook`. This is the single approval point. Wait for a
   go-ahead (or edits) before writing anything.

6. **Write (non-destructive).** On approval:
   - Back up `MEMORY.md` to `MEMORY.md.bak` first.
   - Write each new memory at `.claude/memory/<type>_<slug>.md` in the
     `auto-memory` format. Never overwrite an existing file — pick a new slug
     or update in place by merging.
   - Append one index line per new file to `MEMORY.md`.

7. **Update the manifest.** Write `scanned_sessions` into
   `.claude/memory/.init_manifest.json` under `processed_sessions` (union with
   any existing ids) so the next run is incremental and won't re-mine them.

8. **Report.** State counts only: sessions scanned, candidates proposed,
   memories written, duplicates skipped. Then stop — no narration.

## Pitfalls

1. **Treating `suggested_type` as final.** The extractor flags anything with
   "no/never/stop" as feedback. A "never force-push" rule is feedback; "I never
   use yarn" is a `user` preference. Re-judge every one.
2. **Importing cross-project noise on a global run.** A fact from an unrelated
   repo may not belong in *this* project's memory. When in doubt on a global
   run, prefer facts that recur across projects or are clearly about the user.
3. **Writing before the gate.** The script is read-only by design. If you write
   a single file before step 5, you have broken the one-approval contract.
4. **Skipping the manifest update.** Without step 7, the next `/memory-init`
   re-proposes everything you already imported.
5. **Duplicating `auto-memory`'s format.** Frontmatter at byte 0, `type` in
   {user, feedback, project, reference}, **Why** + **How to apply** present.
6. **Secrets.** Transcripts can contain tokens or keys. The digest stays local
   and is never sent anywhere — keep it that way; do not echo raw secrets into
   a memory file.

## Verification Checklist

- [ ] Scope was chosen by the user, not assumed
- [ ] Extractor ran read-only; no memory file written before the review gate
- [ ] Every candidate re-classified, not trusted from `suggested_type`
- [ ] Deduped against existing `.claude/memory/` and `MEMORY.md`
- [ ] One review gate shown; user approved before any write
- [ ] `MEMORY.md` backed up to `MEMORY.md.bak` before edit
- [ ] Each new file in `auto-memory` format with **Why** / **How to apply**
- [ ] `.init_manifest.json` updated with the scanned session ids
- [ ] Report is counts-only; no per-save announcements
