import json

from avatar_engine.jobs.service import JobService
from avatar_engine.jobs.worker import Worker


def test_fake_pipeline_manifest_flags(settings) -> None:
    service = JobService(settings)
    job_id = service.create_fake_job(dry_run=True)
    Worker(settings).run_once()
    manifest_path = settings.data_dir / "jobs" / job_id / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["production_accepted"] is False
    assert manifest["operator_visual_review"] == "pending"
    assert manifest["real_generation_executed"] is False
    assert manifest["comfyui_submit_executed"] is False
    assert manifest["automatic_retry_executed"] is False
