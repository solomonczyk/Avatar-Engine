from avatar_engine.jobs.service import JobService
from avatar_engine.jobs.worker import Worker


def test_talking_head_worker_creates_required_artifacts(settings, sample_reference_image, sample_audio) -> None:
    job_id = JobService(settings).create_talking_head_job(
        reference_image=str(sample_reference_image),
        audio=str(sample_audio),
        allow_fake_runtime=True,
    )
    Worker(settings).run_once(mode="talking-head")
    job_dir = settings.data_dir / "jobs" / job_id

    assert (job_dir / "input" / "reference" / "reference.png").exists()
    assert (job_dir / "input" / "audio" / "audio_16khz_mono.wav").exists()
    assert (job_dir / "output" / f"{job_id}_talking_head.mp4").exists()
    assert (job_dir / "preview" / "contact_sheet.png").exists()
    assert (job_dir / "operator_review_packet.json").exists()
