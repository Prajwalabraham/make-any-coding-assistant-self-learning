from __future__ import annotations

import json
from collections.abc import Iterator
from dataclasses import dataclass
from enum import IntEnum, StrEnum
from pathlib import Path
from typing import Protocol


class RecordType(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"


class Scope(StrEnum):
    LOCAL = "local"
    GLOBAL = "global"


class Cap(IntEnum):
    MAX_CANDIDATES = 120
    MAX_TEXT_CHARS = 700
    MIN_TEXT_CHARS = 12
    MAX_SESSIONS = 2000


class ExtractionError(Exception):
    pass


class TranscriptStoreNotFoundError(ExtractionError):
    pass


@dataclass(slots=True, frozen=True)
class SessionRef:
    session_id: str
    path: Path
    mtime: float


class TranscriptSource(Protocol):
    def iter_sessions(self, store: Path) -> Iterator[SessionRef]: ...

    def iter_records(self, ref: SessionRef) -> Iterator[dict[str, object]]: ...

    def session_cwd(self, ref: SessionRef) -> str: ...


class ClaudeCodeSource:
    def iter_sessions(self, store: Path) -> Iterator[SessionRef]:
        if not store.is_dir():
            raise TranscriptStoreNotFoundError(str(store))
        for path in sorted(store.glob("*/*.jsonl"), key=_mtime, reverse=True):
            yield SessionRef(path.stem, path, _mtime(path))

    def iter_records(self, ref: SessionRef) -> Iterator[dict[str, object]]:
        with ref.path.open(encoding="utf-8", errors="replace") as handle:
            for line in handle:
                record = safe_json(line)
                if record is not None:
                    yield record

    def session_cwd(self, ref: SessionRef) -> str:
        for record in self.iter_records(ref):
            cwd = record_cwd(record)
            if cwd:
                return cwd
        return ""


def _mtime(path: Path) -> float:
    try:
        return path.stat().st_mtime
    except OSError:
        return 0.0


def safe_json(line: str) -> dict[str, object] | None:
    stripped = line.strip()
    if not stripped:
        return None
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def record_cwd(record: dict[str, object]) -> str:
    cwd = record.get("cwd")
    return cwd if isinstance(cwd, str) else ""


def default_store() -> Path:
    return Path.home() / ".claude" / "projects"
