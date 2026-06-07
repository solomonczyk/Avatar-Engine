from avatar_engine.integrations.comfyui.workflow_patcher import patch_controlled_inputs


def test_complete_workflow_patch_report_has_no_missing_targets() -> None:
    workflow = {
        "3": {"class_type": "KSampler", "inputs": {"seed": 1, "steps": 1, "cfg": 1, "sampler_name": "euler", "scheduler": "normal"}},
        "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "old.safetensors"}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"width": 1, "height": 1, "batch_size": 1}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": "old"}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"text": "old"}},
        "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": "old"}},
    }

    _patched, report = patch_controlled_inputs(
        workflow,
        checkpoint="new.safetensors",
        positive_prompt="p",
        negative_prompt="n",
        seed=2,
        width=512,
        height=512,
        steps=15,
        cfg=6.5,
        output_prefix="avatar_engine/job",
    )

    assert report.missing_targets == []
    assert len(report.patched_fields) == 12
    assert report.workflow_changed is True
