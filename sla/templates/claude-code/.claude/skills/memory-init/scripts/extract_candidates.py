#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Iterator, Sequence
from hashlib import sha1
from pathlib import Path

from models import CUE_TO_TYPE, Candidate, CueKind, Digest, MemoryType, Settings
from transcript import (
    Cap,
    ClaudeCodeSource,
    RecordType,
    Scope,
    SessionRef,
    TranscriptSource,
    TranscriptStoreNotFoundError,
    default_store,
    record_cwd,
    safe_json,
)


_CORRECTION = re.compile(
    r"\b(no,?\s|don't|do not|stop|never|wrong|incorrect|that's not|please don't)\b",
    re.I,
)
_CONFIRMATION = re.compile(
    r"\b(yes,?\s+exactly|perfect|that's right|keep doing|good call|that worked|love it)\b",
    re.I,
)
_PREFERENCE = re.compile(
    r"\b(i (?:prefer|like|always|usually|never)|from now on|going forward|"
    r"in this (?:repo|project)|our (?:team|convention)|we use|we follow)\b",
    re.I,
)
_REFERENCE = re.compile(
    r"\b(linear|jira|grafana|datadog|slack channel|notion|confluence|runbook|dashboard at|sentry|pagerduty)\b",
    re.I,
)
_WRAPPER = re.compile(r"^\s*<(command-name|command-message|command-args|local-command-stdout|user-prompt-submit-hook)\b")
_REMINDER = re.compile(r"<system-reminder>.*?</system-reminder>", re.S)
_WHITESPACE = re.compile(r"\s+")


def _human_text(message: object) -> str:
    if not isinstance(message, dict):
        return ""
    content = message.get("content")
    if isinstance(content, str):
        return _clean(content)
    if isinstance(content, list):
        return _clean(" ".join(_text_blocks(content)))
    return ""


def _text_blocks(content: Sequence[object]) -> Iterator[str]:
    for block in content:
        if isinstance(block, dict) and block.get("type") == "text":
            value = block.get("text")
            if isinstance(value, str):
                yield value


def _clean(text: str) -> str:
    without_reminders = _REMINDER.sub(" ", text)
    return _WHITESPACE.sub(" ", without_reminders).strip()


def _is_genuine(text: str) -> bool:
    return bool(text) and not _WRAPPER.match(text) and len(text) >= int(Cap.MIN_TEXT_CHARS)


def _detect(text: str) -> tuple[CueKind, ...]:
    cues: list[CueKind] = []
    if _CORRECTION.search(text):
        cues.append(CueKind.CORRECTION)
    if _CONFIRMATION.search(text):
        cues.append(CueKind.CONFIRMATION)
    if _PREFERENCE.search(text):
        cues.append(CueKind.PREFERENCE)
    if _REFERENCE.search(text):
        cues.append(CueKind.EXTERNAL_REFERENCE)
    return tuple(cues)


def _suggest(cues: Sequence[CueKind]) -> MemoryType:
    for cue in cues:
        if cue is not CueKind.CONFIRMATION:
            return CUE_TO_TYPE[cue]
    return MemoryType.FEEDBACK


def _fingerprint(text: str) -> str:
    return sha1(text.lower().encode("utf-8")).hexdigest()


def _project_name(cwd: str, fallback: str) -> str:
    return Path(cwd).name if cwd else fallback


def _in_scope(cwd: str, settings: Settings) -> bool:
    if settings.scope is Scope.GLOBAL:
        return True
    return Path(cwd) == settings.project_root if cwd else False


def _candidate(record: dict[str, object], settings: Settings) -> Candidate | None:
    if bool(record.get("isMeta")) or bool(record.get("isSidechain")):
        return None
    if record.get("type") != RecordType.USER:
        return None
    cwd = record_cwd(record)
    if not _in_scope(cwd, settings):
        return None
    text = _human_text(record.get("message"))[: int(Cap.MAX_TEXT_CHARS)]
    if not _is_genuine(text):
        return None
    cues = _detect(text)
    if not cues:
        return None
    return _build(record, settings, cwd, text, cues)


def _build(
    record: dict[str, object],
    settings: Settings,
    cwd: str,
    text: str,
    cues: tuple[CueKind, ...],
) -> Candidate:
    return Candidate(
        text=text,
        suggested_type=_suggest(cues),
        cues=cues,
        session_id=str(record.get("sessionId") or ""),
        project=_project_name(cwd, settings.project_root.name),
        timestamp=str(record.get("timestamp") or ""),
        fingerprint=_fingerprint(text),
    )


def _collect(source: TranscriptSource, settings: Settings) -> Digest:
    seen: set[str] = set()
    kept: list[Candidate] = []
    scanned: list[str] = []
    skipped = 0
    found = 0
    for ref in _bounded(source.iter_sessions(settings.store)):
        if ref.session_id in settings.processed or not _in_scope(source.session_cwd(ref), settings):
            skipped += 1
            continue
        scanned.append(ref.session_id)
        found += _scan_session(source, ref, settings, seen, kept)
    return _finalize(settings, tuple(kept), tuple(scanned), len(scanned), skipped, found)


def _scan_session(
    source: TranscriptSource,
    ref: SessionRef,
    settings: Settings,
    seen: set[str],
    kept: list[Candidate],
) -> int:
    found = 0
    for record in source.iter_records(ref):
        candidate = _candidate(record, settings)
        if candidate is None:
            continue
        found += 1
        if candidate.fingerprint not in seen:
            seen.add(candidate.fingerprint)
            kept.append(candidate)
    return found


def _bounded(sessions: Iterator[SessionRef]) -> Iterator[SessionRef]:
    for index, ref in enumerate(sessions):
        if index >= int(Cap.MAX_SESSIONS):
            return
        yield ref


def _finalize(
    settings: Settings,
    kept: tuple[Candidate, ...],
    scanned: tuple[str, ...],
    sessions_scanned: int,
    skipped: int,
    found: int,
) -> Digest:
    window = kept[: settings.max_candidates]
    return Digest(
        scope=settings.scope,
        candidates=window,
        scanned_sessions=scanned,
        sessions_scanned=sessions_scanned,
        sessions_skipped=skipped,
        candidates_found=found,
        candidates_dropped=len(kept) - len(window),
    )


def _serialize(digest: Digest) -> str:
    payload = {
        "scope": str(digest.scope),
        "sessions_scanned": digest.sessions_scanned,
        "sessions_skipped": digest.sessions_skipped,
        "candidates_found": digest.candidates_found,
        "candidates_dropped": digest.candidates_dropped,
        "scanned_sessions": list(digest.scanned_sessions),
        "candidates": [_candidate_dict(item) for item in digest.candidates],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


def _candidate_dict(item: Candidate) -> dict[str, object]:
    return {
        "text": item.text,
        "suggested_type": str(item.suggested_type),
        "cues": [str(cue) for cue in item.cues],
        "session_id": item.session_id,
        "project": item.project,
        "timestamp": item.timestamp,
        "fingerprint": item.fingerprint,
    }


def _load_processed(path: Path | None) -> frozenset[str]:
    if path is None or not path.is_file():
        return frozenset()
    record = safe_json(path.read_text(encoding="utf-8"))
    ids = record.get("processed_sessions") if record else None
    return frozenset(ids) if isinstance(ids, list) else frozenset()


def _parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mine Claude Code transcripts into memory candidates.")
    parser.add_argument("--scope", choices=tuple(Scope), type=Scope, default=Scope.LOCAL)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--store", type=Path, default=default_store())
    parser.add_argument("--manifest", type=Path, default=None)
    parser.add_argument("--max-candidates", type=int, default=int(Cap.MAX_CANDIDATES))
    return parser.parse_args(argv)


def _build_settings(args: argparse.Namespace) -> Settings:
    return Settings(
        scope=args.scope,
        project_root=args.project_root.resolve(),
        store=args.store,
        processed=_load_processed(args.manifest),
        max_candidates=args.max_candidates,
    )


def _emit(text: str) -> None:
    sys.stdout.buffer.write(text.encode("utf-8"))
    sys.stdout.buffer.flush()


def main(argv: Sequence[str]) -> int:
    settings = _build_settings(_parse_args(argv))
    try:
        digest = _collect(ClaudeCodeSource(), settings)
    except TranscriptStoreNotFoundError as error:
        _emit(json.dumps({"error": "store_not_found", "store": str(error)}))
        return 1
    _emit(_serialize(digest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
