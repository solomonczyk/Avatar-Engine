from avatar_engine.jobs.repository import JobRepository
from avatar_engine.pipeline.runner import PipelineRunner
from avatar_engine.pipeline.stages.base import StageResult


class OkStage:
    name = "ok"
    uses_gpu = False

    def run(self, context):
        return StageResult(stdout="ok")


class FailStage:
    name = "fail"
    uses_gpu = False

    def run(self, context):
        return StageResult(status="failed", error_message="planned failure")


class LaterStage:
    name = "later"
    uses_gpu = False

    def run(self, context):
        return StageResult(stdout="later")


def test_failed_stage_stops_pipeline_and_skips_remaining(settings) -> None:
    repo = JobRepository(settings.db_path)
    job_id = repo.create_job({"mode": "fake"}, ["ok", "fail", "later"])
    assert repo.claim_next_job() == job_id
    PipelineRunner(settings, repo, [OkStage(), FailStage(), LaterStage()]).run(job_id)
    job = repo.get_job(job_id)
    stages = {stage.stage_name: stage for stage in repo.get_stages(job_id)}
    assert job.status == "failed"
    assert stages["fail"].status == "failed"
    assert stages["later"].status == "skipped"
    assert job.retry_count == 0
