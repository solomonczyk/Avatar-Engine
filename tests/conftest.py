from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from avatar_engine.config import Settings
from avatar_engine.integrations.talking_head.audio import write_test_tone


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


@pytest.fixture()
def sample_reference_image(tmp_path: Path) -> Path:
    path = tmp_path / "reference.png"
    image = Image.new("RGB", (96, 96), "white")
    for x in range(28, 68):
        for y in range(20, 72):
            image.putpixel((x, y), (210, 160, 130))
    for x in range(38, 46):
        for y in range(40, 46):
            image.putpixel((x, y), (20, 20, 20))
    for x in range(54, 62):
        for y in range(40, 46):
            image.putpixel((x, y), (20, 20, 20))
    image.save(path)
    return path


@pytest.fixture()
def sample_audio(tmp_path: Path) -> Path:
    path = tmp_path / "voice.wav"
    write_test_tone(path)
    return path
