from avatar_engine.integrations.comfyui.workflow_patcher import patch_workflow


def test_patch_workflow_dotted_paths_without_mutating_source() -> None:
    original = {"nodes": [{"inputs": {"seed": 1}}]}
    patched = patch_workflow(original, {"nodes.0.inputs.seed": 42})
    assert patched["nodes"][0]["inputs"]["seed"] == 42
    assert original["nodes"][0]["inputs"]["seed"] == 1
