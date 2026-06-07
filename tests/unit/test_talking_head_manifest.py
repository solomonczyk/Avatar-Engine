import json

from avatar_engine.jobs.service import JobService
from avatar_engine.jobs.worker import Worker


def test_talking_head_manifest_flags(settings, sample_reference_image, sample_audio) -> None:
    job_id = JobService(settings).create_talking_head_job(
        reference_image=str(sample_reference_image),
        audio=str(sample_audio),
        allow_fake_runtime=True,
    )
    Worker(settings).run_once(mode="talking-head")

    manifest = json.loads((settings.data_dir / "jobs" / job_id / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["reference_image_mode"] == "job_input"
    assert manifest["reference_image_hardcoded"] is False
    assert manifest["system_bound_to_single_reference"] is False
    assert manifest["talking_head_attempts"] == 1
    assert manifest["max_talking_head_generations"] == 1
    assert manifest["automatic_retry_executed"] is False
    assert manifest["new_face_generated"] is False
    assert manifest["face_swap_executed"] is False
    assert manifest["operator_visual_review_required"] is True
    assert manifest["production_accepted"] is False
