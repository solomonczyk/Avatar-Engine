from __future__ import annotations

from avatar_engine.config import Settings, get_settings
from avatar_engine.jobs.repository import JobRepository
from avatar_engine.pipeline.runner import PipelineRunner, fake_stages
from avatar_engine.pipeline.stages.comfyui_image import comfyui_image_stages


class Worker:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self.repository = JobRepository(self.settings.db_path)

    def run_once(self, mode: str = "fake") -> str | None:
        self.settings.ensure_directories()
        self.repository.init()
        requested_mode = mode.replace("-", "_")
        if requested_mode not in {"auto", "fake", "comfyui_image"}:
            raise ValueError("Worker mode must be auto, fake, or comfyui-image")
        job_id = self.repository.claim_next_job(None if requested_mode == "auto" else requested_mode)
        if job_id is None:
            return None
        job = self.repository.get_job(job_id)
        if job is None:
            raise ValueError(f"Unknown job: {job_id}")
        job_mode = str(job.input_json.get("mode", "fake")).replace("-", "_")
        if requested_mode != "auto" and requested_mode != job_mode:
            raise ValueError(f"Queued job mode {job_mode} does not match requested worker mode {requested_mode}")
        if job_mode == "fake":
            stages = fake_stages()
        elif job_mode == "comfyui_image":
            stages = comfyui_image_stages()
        else:
            raise ValueError(f"Unsupported job mode: {job_mode}")
        PipelineRunner(self.settings, self.repository, stages).run(job_id)
        return job_id
