from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from avatar_engine.config import Settings
from avatar_engine.models import Artifact


@dataclass
class PipelineContext:
    job_id: str
    project_root: Path
    job_dir: Path
    input_dir: Path
    work_dir: Path
    output_dir: Path
    logs_dir: Path
    config: Settings
    artifacts: list[Artifact] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(cls, job_id: str, settings: Settings) -> "PipelineContext":
        assert settings.data_dir is not None
        job_dir = settings.data_dir / "jobs" / job_id
        context = cls(
            job_id=job_id,
            project_root=settings.project_root,
            job_dir=job_dir,
            input_dir=job_dir / "input",
            work_dir=job_dir / "work",
            output_dir=job_dir / "output",
            logs_dir=job_dir / "logs",
            config=settings,
        )
        for path in [context.job_dir, context.input_dir, context.work_dir, context.output_dir, context.logs_dir]:
            path.mkdir(parents=True, exist_ok=True)
        return context
