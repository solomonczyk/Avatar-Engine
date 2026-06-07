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

    def create_comfyui_image_job(
        self,
        *,
        workflow: str,
        prompt: str,
        negative_prompt: str,
        checkpoint: str | None = None,
        seed: int = 20260607,
        width: int = 512,
        height: int = 512,
        steps: int = 15,
        cfg: float = 6.5,
        sampler: str = "euler",
        scheduler: str = "normal",
        timeout_seconds: float = 900,
        poll_interval: float = 2,
    ) -> str:
        from avatar_engine.pipeline.stages.comfyui_image import comfyui_image_stage_names

        self.init_db()
        input_data: dict[str, Any] = {
            "mode": "comfyui_image",
            "workflow": workflow,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "checkpoint": checkpoint,
            "seed": seed,
            "width": width,
            "height": height,
            "steps": steps,
            "cfg": cfg,
            "sampler": sampler,
            "scheduler": scheduler,
            "batch_size": 1,
            "images_requested": 1,
            "max_generations": 1,
            "automatic_retry": False,
            "timeout_seconds": timeout_seconds,
            "poll_interval": poll_interval,
        }
        return self.repository.create_job(input_data, comfyui_image_stage_names())
