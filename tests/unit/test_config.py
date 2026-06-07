from avatar_engine.config import Settings


def test_config_defaults_support_windows_space(settings: Settings) -> None:
    settings.ensure_directories()
    assert settings.gpu_worker_concurrency == 1
    assert settings.auto_retry is False
    assert "avatar_engine.db" in str(settings.db_path)
    assert settings.data_dir.exists()
