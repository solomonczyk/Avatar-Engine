from avatar_engine.jobs.repository import JobRepository
from avatar_engine.jobs.service import JobService


def test_job_survives_repository_restart(settings) -> None:
    job_id = JobService(settings).create_fake_job(dry_run=True)
    restarted_repo = JobRepository(settings.db_path)
    job = restarted_repo.get_job(job_id)
    assert job is not None
    assert job.status == "queued"
