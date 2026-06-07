from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

from avatar_engine.models import Artifact
from avatar_engine.pipeline.context import PipelineContext


@dataclass
class StageResult:
    status: str = "completed"
    artifacts: list[Artifact] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    stdout: str = ""
    stderr: str = ""
    error_message: str | None = None


class PipelineStage(Protocol):
    name: str
    uses_gpu: bool

    def run(self, context: PipelineContext) -> StageResult:
        ...


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def text_artifact(context: PipelineContext, stage_name: str, artifact_type: str, filename: str, content: str) -> Artifact:
    path = context.output_dir / filename
    path.write_text(content, encoding="utf-8")
    return Artifact(
        artifact_type=artifact_type,
        path=path,
        sha256=sha256_file(path),
        size_bytes=path.stat().st_size,
        stage_name=stage_name,
    )
