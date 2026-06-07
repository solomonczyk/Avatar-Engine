from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Artifact:
    artifact_type: str
    path: Path
    sha256: str = ""
    size_bytes: int = 0
    stage_name: str = ""


@dataclass(frozen=True)
class Job:
    id: str
    created_at: str
    updated_at: str
    status: str
    current_stage: str | None
    input_json: dict[str, Any]
    output_json: dict[str, Any]
    error_message: str | None
    retry_count: int


@dataclass(frozen=True)
class JobStage:
    id: int
    job_id: str
    stage_name: str
    stage_order: int
    status: str
    started_at: str | None
    finished_at: str | None
    duration_ms: int | None
    stdout_path: str | None
    stderr_path: str | None
    error_message: str | None


@dataclass(frozen=True)
class HealthResult:
    available: bool
    status: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SubmitResult:
    prompt_id: str
    submitted: bool
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class HistoryResult:
    prompt_id: str
    status: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SystemStatsResult:
    received: bool
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ObjectInfoResult:
    received: bool
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ComfyUIOutput:
    prompt_id: str
    node_id: str
    filename: str
    subfolder: str
    output_type: str
