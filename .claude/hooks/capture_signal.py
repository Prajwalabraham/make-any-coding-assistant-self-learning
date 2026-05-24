#!/usr/bin/env python3
"""Forces the model to consider saving on every turn that looks like signal.

The model is perfectly capable of recognising corrections and preferences,
but it forgets to act on that recognition roughly half the time when no
external prompt asks the question. A cheap regex pass plus a one-line
nudge in additionalContext closes that gap without taking the decision
away from the model.

Counter state is kept so a recurring pattern can also trigger the
skill-distiller promotion rule (three repeats = candidate workflow).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COUNTER_FILE = ROOT / "memory" / ".signal_counter.json"

CORRECTION = re.compile(
    r"\b(no,?\s|don't|do not|stop|never|wrong|incorrect|that's not|please don't)\b",
    re.I,
)
CONFIRMATION = re.compile(
    r"\b(yes,?\s+exactly|perfect|that's right|keep doing|nice|good call|"
    r"that worked|love it)\b",
    re.I,
)
PREFERENCE = re.compile(
    r"\b(i (?:prefer|like|always|usually|never)|from now on|going forward|"
    r"in this (?:repo|project)|our (?:team|convention))\b",
    re.I,
)
REFERENCE = re.compile(
    r"\b(linear|jira|grafana|datadog|slack channel|notion|confluence|"
    r"runbook|dashboard at)\b",
    re.I,
)


def detect(prompt: str) -> list[str]:
    cues = []
    if CORRECTION.search(prompt):
        cues.append("correction")
    if CONFIRMATION.search(prompt):
        cues.append("confirmation")
    if PREFERENCE.search(prompt):
        cues.append("preference")
    if REFERENCE.search(prompt):
        cues.append("external-reference")
    return cues


def bump_counter(cue_key: str) -> int:
    # Persisting between turns is what makes the "3 repeats" promotion
    # rule possible. In-memory counters reset every session and would
    # never reach the threshold.
    COUNTER_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        data = json.loads(COUNTER_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    data[cue_key] = data.get(cue_key, 0) + 1
    COUNTER_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data[cue_key]


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return
    prompt = (payload.get("prompt") or "").strip()
    if not prompt:
        return

    cues = detect(prompt)
    if not cues:
        return

    cue_key = ",".join(sorted(cues))
    count = bump_counter(cue_key)

    msg = (
        f"[self-learning] Signal detected ({', '.join(cues)}). "
        f"Before responding, decide whether to invoke the `auto-memory` skill. "
        f"This cue pattern has fired {count} time(s)."
    )
    if count >= 3 and "correction" in cues:
        msg += (
            " Pattern has repeated 3+ times, also consider `skill-distiller` "
            "to lift the underlying workflow into a skill."
        )

    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": msg,
            }
        },
        sys.stdout,
    )


if __name__ == "__main__":
    main()
