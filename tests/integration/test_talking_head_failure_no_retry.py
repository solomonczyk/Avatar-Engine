import json

from avatar_engine.jobs.service import JobService
from avatar_engine.jobs.worker import Worker


def test_talking_head_missing_runtime_stops_before_attempt(settings, sample_reference_image, sample_audio) -> None:
    job_id = JobService(settings).create_talking_head_job(
        reference_image=str(sample_reference_image),
        audio=str(sample_audio),
    )
    Worker(settings).run_once(mode="talking-head")
    job = JobService(settings).repository.get_job(job_id)
    selection = json.loads(
        (settings.data_dir / "jobs" / job_id / "preflight" / "talking_head_runtime_selection.json").read_text(encoding="utf-8")
    )

    assert job.status == "failed"
    assert selection["execution_allowed"] is False
    assert "runtime_command.json" not in {path.name for path in (settings.data_dir / "jobs" / job_id / "logs").glob("*")}
