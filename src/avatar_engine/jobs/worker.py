from __future__ import annotations

from avatar_engine.config import Settings, get_settings
from avatar_engine.jobs.repository import JobRepository
from avatar_engine.pipeline.runner import PipelineRunner, fake_stages


class Worker:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self.repository = JobRepository(self.settings.db_path)

    def run_once(self, mode: str = "fake") -> str | None:
        self.settings.ensure_directories()
        self.repository.init()
        if mode != "fake":
            raise ValueError("Only fake mode is allowed in the bootstrap layer")
        job_id = self.repository.claim_next_job()
        if job_id is None:
            return None
        PipelineRunner(self.settings, self.repository, fake_stages()).run(job_id)
        return job_id
