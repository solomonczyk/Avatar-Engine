import json
from pathlib import Path

from avatar_engine.jobs.service import JobService
from avatar_engine.jobs.worker import Worker


def test_talking_head_output_stays_inside_job(settings, sample_reference_image, sample_audio) -> None:
    job_id = JobService(settings).create_talking_head_job(
        reference_image=str(sample_reference_image),
        audio=str(sample_audio),
        allow_fake_runtime=True,
    )
    Worker(settings).run_once(mode="talking-head")
    manifest = json.loads((settings.data_dir / "jobs" / job_id / "manifest.json").read_text(encoding="utf-8"))
    output_video = Path(manifest["output_video"])

    assert settings.data_dir / "jobs" / job_id in output_video.parents
    assert output_video.name == f"{job_id}_talking_head.mp4"
