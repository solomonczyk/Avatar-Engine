from avatar_engine.integrations.talking_head.runtime import discover_runtime_candidates


def test_runtime_selection_blocks_when_no_ready_runtime(settings) -> None:
    selection = discover_runtime_candidates(settings.project_root, settings.project_root / "missing-comfy")

    assert selection["execution_allowed"] is False
    assert selection["real_talking_head_generation_executed"] is False
    assert selection["next_allowed_action"] == "talking_head_runtime_asset_authorization_required"


def test_fake_runtime_selection_is_explicit(settings) -> None:
    selection = discover_runtime_candidates(settings.project_root, settings.project_root / "missing-comfy", allow_fake_runtime=True)

    assert selection["execution_allowed"] is True
    assert selection["selected_runtime"] == "fake_talking_head"
