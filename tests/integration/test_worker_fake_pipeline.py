from avatar_engine.jobs.service import JobService
from avatar_engine.jobs.worker import Worker


def test_worker_runs_fake_pipeline_to_operator_review(settings) -> None:
    job_id = JobService(settings).create_fake_job(dry_run=True)
    assert Worker(settings).run_once(mode="fake") == job_id
    job = JobService(settings).repository.get_job(job_id)
    assert job.status == "operator_visual_review_required"
    assert job.retry_count == 0
