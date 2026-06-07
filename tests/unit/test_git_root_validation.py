from pathlib import Path


def test_repository_root_is_standalone_avatar_engine() -> None:
    root = Path(__file__).resolve().parents[2]
    assert root.name == "Avatar Engine"
    assert (root / ".git").exists()
