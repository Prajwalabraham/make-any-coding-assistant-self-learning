from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

from transcript import Cap, Scope


class MemoryType(StrEnum):
    USER = "user"
    FEEDBACK = "feedback"
    PROJECT = "project"
    REFERENCE = "reference"


class CueKind(StrEnum):
    CORRECTION = "correction"
    CONFIRMATION = "confirmation"
    PREFERENCE = "preference"
    EXTERNAL_REFERENCE = "external-reference"


CUE_TO_TYPE: dict[CueKind, MemoryType] = {
    CueKind.CORRECTION: MemoryType.FEEDBACK,
    CueKind.CONFIRMATION: MemoryType.FEEDBACK,
    CueKind.PREFERENCE: MemoryType.USER,
    CueKind.EXTERNAL_REFERENCE: MemoryType.REFERENCE,
}


@dataclass(slots=True, frozen=True)
class Candidate:
    text: str
    suggested_type: MemoryType
    cues: tuple[CueKind, ...]
    session_id: str
    project: str
    timestamp: str
    fingerprint: str


@dataclass(slots=True, frozen=True)
class Digest:
    scope: Scope
    candidates: tuple[Candidate, ...]
    scanned_sessions: tuple[str, ...]
    sessions_scanned: int
    sessions_skipped: int
    candidates_found: int
    candidates_dropped: int


@dataclass(slots=True, frozen=True)
class Settings:
    scope: Scope
    project_root: Path
    store: Path
    processed: frozenset[str]
    max_candidates: int = field(default=int(Cap.MAX_CANDIDATES))
