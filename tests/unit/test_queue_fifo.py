from avatar_engine.jobs.repository import JobRepository


def test_queue_claims_oldest_job_first(settings) -> None:
    repo = JobRepository(settings.db_path)
    first = repo.create_job({"n": 1}, ["stage"])
    second = repo.create_job({"n": 2}, ["stage"])
    assert repo.claim_next_job() == first
    assert repo.claim_next_job() is None
    assert repo.get_job(second).status == "queued"
