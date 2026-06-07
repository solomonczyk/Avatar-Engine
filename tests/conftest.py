from __future__ import annotations

from pathlib import Path

import pytest

from avatar_engine.config import Settings


@pytest.fixture()
def settings(tmp_path: Path) -> Settings:
    return Settings(
        PROJECT_ROOT=tmp_path,
        DATA_DIR=tmp_path / "data",
        DB_PATH=tmp_path / "data" / "avatar_engine.db",
        GPU_LOCK_PATH=tmp_path / "data" / "runtime" / "gpu.lock",
        GPU_WORKER_CONCURRENCY=1,
        AUTO_RETRY=False,
    )
