from avatar_engine.jobs.service import JobService
from avatar_engine.jobs.worker import Worker


def test_talking_head_fake_runtime_reaches_review(settings, sample_reference_image, sample_audio) -> None:
    job_id = JobService(settings).create_talking_head_job(
        reference_image=str(sample_reference_image),
        audio=str(sample_audio),
        allow_fake_runtime=True,
    )

    assert Worker(settings).run_once(mode="talking-head") == job_id
    job = JobService(settings).repository.get_job(job_id)
    assert job.status == "operator_visual_review_required"
