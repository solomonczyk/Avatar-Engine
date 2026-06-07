from __future__ import annotations

from pathlib import Path
from typing import Any

from avatar_engine.config import Settings, get_settings
from avatar_engine.jobs.repository import JobRepository
from avatar_engine.pipeline.runner import fake_stage_names


class JobService:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self.repository = JobRepository(self.settings.db_path)

    def init_db(self) -> None:
        self.settings.ensure_directories()
        self.repository.init()

    def create_fake_job(
        self,
        *,
        portrait: str | None = None,
        audio: str | None = None,
        dry_run: bool = False,
        mode: str = "fake",
    ) -> str:
        self.init_db()
        input_data: dict[str, Any] = {
            "mode": mode,
            "dry_run": dry_run,
            "portrait": portrait,
            "audio": audio,
        }
        if dry_run:
            input_data["portrait"] = str(Path("data/input/dry_run_portrait.txt"))
            input_data["audio"] = str(Path("data/input/dry_run_audio.txt"))
        return self.repository.create_job(input_data, fake_stage_names())
