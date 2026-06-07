from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def default_project_root() -> Path:
    return Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    project_root: Path = Field(default_factory=default_project_root, alias="PROJECT_ROOT")
    data_dir: Path | None = Field(default=None, alias="DATA_DIR")
    db_path: Path | None = Field(default=None, alias="DB_PATH")
    comfyui_base_url: str = Field(default="http://127.0.0.1:8188", alias="COMFYUI_BASE_URL")
    comfyui_root: Path = Field(default=Path("F:/ComfyUI"), alias="COMFYUI_ROOT")
    ffmpeg_path: str = Field(default="ffmpeg", alias="FFMPEG_PATH")
    gpu_worker_concurrency: int = Field(default=1, alias="GPU_WORKER_CONCURRENCY")
    auto_retry: bool = Field(default=False, alias="AUTO_RETRY")
    gpu_lock_path: Path | None = Field(default=None, alias="GPU_LOCK_PATH")

    @model_validator(mode="after")
    def fill_paths(self) -> "Settings":
        self.project_root = self.project_root.resolve()
        if self.data_dir is None:
            self.data_dir = self.project_root / "data"
        if self.db_path is None:
            self.db_path = self.data_dir / "avatar_engine.db"
        if self.gpu_lock_path is None:
            self.gpu_lock_path = self.data_dir / "runtime" / "gpu.lock"
        return self

    def ensure_directories(self) -> None:
        assert self.data_dir is not None
        for path in [
            self.data_dir,
            self.data_dir / "input",
            self.data_dir / "jobs",
            self.data_dir / "output",
            self.data_dir / "logs",
            self.data_dir / "runtime",
        ]:
            path.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()
