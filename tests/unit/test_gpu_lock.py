import json

from avatar_engine.resources.gpu_lock import GpuLock, GpuLockBusy, stale_lock_payload


def test_gpu_lock_blocks_second_worker(settings) -> None:
    first = GpuLock(settings.gpu_lock_path)
    first.acquire("job-1", "gpu_stage")
    try:
        second = GpuLock(settings.gpu_lock_path)
        try:
            second.acquire("job-2", "gpu_stage")
            assert False, "second lock should fail"
        except GpuLockBusy:
            pass
    finally:
        first.release()


def test_stale_lock_detects_missing_pid(settings) -> None:
    settings.gpu_lock_path.parent.mkdir(parents=True, exist_ok=True)
    settings.gpu_lock_path.write_text(
        json.dumps({"pid": 0, "job_id": "job-x", "stage": "gpu", "started_at": "now"}),
        encoding="utf-8",
    )
    payload = stale_lock_payload(settings.gpu_lock_path)
    assert payload is not None
    assert payload["job_id"] == "job-x"
