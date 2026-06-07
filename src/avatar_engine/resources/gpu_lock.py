from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from filelock import FileLock, Timeout

from avatar_engine.jobs.repository import utc_now


@dataclass(frozen=True)
class GpuLockInfo:
    pid: int
    job_id: str
    stage: str
    started_at: str


class GpuLockBusy(RuntimeError):
    pass


class GpuLock:
    def __init__(self, path: Path):
        self.path = path
        self.guard_path = path.with_suffix(path.suffix + ".guard")
        self._guard = FileLock(str(self.guard_path), timeout=0)

    def acquire(self, job_id: str, stage: str) -> GpuLockInfo:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self._guard.acquire(timeout=0)
        except Timeout as exc:
            raise GpuLockBusy("GPU lock is already held") from exc
        info = GpuLockInfo(pid=os.getpid(), job_id=job_id, stage=stage, started_at=utc_now())
        self.path.write_text(json.dumps(info.__dict__, indent=2), encoding="utf-8")
        return info

    def release(self) -> None:
        try:
            if self.path.exists():
                self.path.unlink()
        finally:
            if self._guard.is_locked:
                self._guard.release()

    def __enter__(self) -> "GpuLock":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.release()


def read_lock(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def pid_exists(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def stale_lock_payload(path: Path) -> dict[str, object] | None:
    payload = read_lock(path)
    if not payload:
        return None
    pid = int(payload.get("pid", 0))
    return payload if not pid_exists(pid) else None
