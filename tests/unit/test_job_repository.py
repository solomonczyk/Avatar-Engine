from avatar_engine.jobs.repository import JobRepository
from avatar_engine.jobs.state import JobState


def test_repository_initializes_and_persists_job(settings) -> None:
    repo = JobRepository(settings.db_path)
    repo.init()
    job_id = repo.create_job({"mode": "fake"}, ["one", "two"])
    job = repo.get_job(job_id)
    assert settings.db_path.exists()
    assert job is not None
    assert job.status == JobState.QUEUED.value
    assert job.retry_count == 0
    assert len(repo.get_stages(job_id)) == 2
