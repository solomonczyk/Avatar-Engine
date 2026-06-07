from avatar_engine.integrations.comfyui.workflow_patcher import patch_controlled_inputs, patch_workflow


def test_patch_workflow_dotted_paths_without_mutating_source() -> None:
    original = {"nodes": [{"inputs": {"seed": 1}}]}
    patched = patch_workflow(original, {"nodes.0.inputs.seed": 42})
    assert patched["nodes"][0]["inputs"]["seed"] == 42
    assert original["nodes"][0]["inputs"]["seed"] == 1


def test_controlled_patch_reports_missing_targets() -> None:
    patched, report = patch_controlled_inputs(
        {"4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "old.safetensors"}}},
        checkpoint="new.safetensors",
        positive_prompt="positive",
        negative_prompt="negative",
        seed=1,
        width=512,
        height=512,
        steps=15,
        cfg=6.5,
        output_prefix="avatar_engine/test",
    )

    assert patched["4"]["inputs"]["ckpt_name"] == "new.safetensors"
    assert "4.inputs.ckpt_name" in report.patched_fields
    assert report.missing_targets
    assert report.workflow_changed is True
