from __future__ import annotations

import traceback
from time import perf_counter

from avatar_engine.config import Settings
from avatar_engine.jobs.repository import JobRepository, utc_now
from avatar_engine.jobs.state import JobState, StageState
from avatar_engine.pipeline.context import PipelineContext
from avatar_engine.pipeline.stages.animate_avatar import AnimateAvatarStage
from avatar_engine.pipeline.stages.base import PipelineStage, StageResult
from avatar_engine.pipeline.stages.build_manifest import BuildManifestStage
from avatar_engine.pipeline.stages.prepare_audio import PrepareAudioStage
from avatar_engine.pipeline.stages.prepare_portrait import PreparePortraitStage
from avatar_engine.pipeline.stages.postprocess_video import PostprocessVideoStage
from avatar_engine.pipeline.stages.validate_inputs import ValidateInputsStage
from avatar_engine.resources.gpu_lock import GpuLock


def fake_stages() -> list[PipelineStage]:
    return [
        ValidateInputsStage(),
        PreparePortraitStage(),
        PrepareAudioStage(),
        AnimateAvatarStage(),
        PostprocessVideoStage(),
        BuildManifestStage(),
    ]


def fake_stage_names() -> list[str]:
    return [stage.name for stage in fake_stages()]


class PipelineRunner:
    def __init__(self, settings: Settings, repository: JobRepository, stages: list[PipelineStage]):
        self.settings = settings
        self.repository = repository
        self.stages = stages

    def run(self, job_id: str) -> None:
        job = self.repository.get_job(job_id)
        if job is None:
            raise ValueError(f"Unknown job: {job_id}")
        context = PipelineContext.create(job_id, self.settings)
        context.metadata["job"] = job
        context.metadata["started_at"] = utc_now()
        context.metadata["stage_results"] = []
        worker_log = context.logs_dir / "worker.log"
        worker_log.write_text(f"worker started for {job_id}\n", encoding="utf-8")

        stages_by_name = {stage.stage_name: stage for stage in self.repository.get_stages(job_id)}
        for stage in self.stages:
            stage_record = stages_by_name[stage.name]
            started_at = utc_now()
            stdout_path = context.logs_dir / f"{stage.name}.stdout.txt"
            stderr_path = context.logs_dir / f"{stage.name}.stderr.txt"
            self.repository.update_job(job_id, JobState.RUNNING, current_stage=stage.name)
            self.repository.update_stage(job_id, stage.name, StageState.RUNNING, started_at=started_at)
            timer = perf_counter()
            try:
                if stage.uses_gpu:
                    lock = GpuLock(self.settings.gpu_lock_path)
                    lock.acquire(job_id, stage.name)
                    try:
                        result = stage.run(context)
                    finally:
                        lock.release()
                else:
                    result = stage.run(context)
            except Exception as exc:  # pragma: no cover - exercised by tests through custom stage
                result = StageResult(status="failed", stderr=traceback.format_exc(), error_message=str(exc))

            duration_ms = int((perf_counter() - timer) * 1000)
            stdout_path.write_text(result.stdout, encoding="utf-8")
            stderr_path.write_text(result.stderr, encoding="utf-8")

            if result.status == "failed":
                self.repository.update_stage(
                    job_id,
                    stage.name,
                    StageState.FAILED,
                    finished_at=utc_now(),
                    duration_ms=duration_ms,
                    stdout_path=str(stdout_path),
                    stderr_path=str(stderr_path),
                    error_message=result.error_message,
                )
                self.repository.skip_remaining_stages(job_id, stage_record.stage_order)
                self.repository.update_job(job_id, JobState.FAILED, current_stage=stage.name, error_message=result.error_message)
                return

            for artifact in result.artifacts:
                context.artifacts.append(artifact)
                self.repository.add_artifact(job_id, stage.name, artifact)
            context.metadata.update(result.metadata)
            context.metadata["stage_results"].append({"name": stage.name, "status": "completed", "duration_ms": duration_ms})
            self.repository.update_stage(
                job_id,
                stage.name,
                StageState.COMPLETED,
                finished_at=utc_now(),
                duration_ms=duration_ms,
                stdout_path=str(stdout_path),
                stderr_path=str(stderr_path),
            )

        self.repository.update_job(
            job_id,
            JobState.OPERATOR_VISUAL_REVIEW_REQUIRED,
            current_stage=None,
            output={
                "manifest_path": str(context.job_dir / "manifest.json"),
                "production_accepted": False,
                "automatic_retry_executed": False,
            },
        )
