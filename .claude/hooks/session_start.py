#!/usr/bin/env python3
"""SessionStart hook: surface the agent's memory + skill inventory.

Reads .claude/SOUL.md, .claude/memory/MEMORY.md, and lists .claude/skills/*.
Emits a single additionalContext block that Claude Code injects into the
session prompt. No network, no side effects.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return ""


def list_skills() -> list[str]:
    skills_dir = ROOT / "skills"
    if not skills_dir.exists():
        return []
    return sorted(p.parent.name for p in skills_dir.glob("*/SKILL.md"))


def build_context() -> str:
    soul = read(ROOT / "SOUL.md")
    index = read(ROOT / "memory" / "MEMORY.md")
    skills = list_skills()

    parts = ["# Self-Learning Agent — Session Bootstrap"]
    if soul:
        parts += ["", "## Persona", soul]
    if index:
        parts += ["", "## Memory Index", index]
    if skills:
        parts += ["", "## Available Skills", *(f"- {s}" for s in skills)]
    parts += [
        "",
        "On every turn: scan memory for relevance, capture new signal via "
        "the `auto-memory` skill, and propose a new skill via `skill-distiller` "
        "when a recipe repeats for the third time.",
    ]
    return "\n".join(parts)


def main() -> None:
    payload = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": build_context(),
        }
    }
    json.dump(payload, sys.stdout)


if __name__ == "__main__":
    main()
