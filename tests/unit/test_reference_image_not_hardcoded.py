from avatar_engine.pipeline.stages.talking_head import normalize_talking_head_inputs


def test_reference_image_not_hardcoded(settings, sample_reference_image, sample_audio) -> None:
    inputs = normalize_talking_head_inputs(
        {
            "mode": "talking_head",
            "reference_image_path": str(sample_reference_image),
            "audio_path": str(sample_audio),
        },
        settings.project_root,
    )

    assert inputs["reference_image_path"] == sample_reference_image
    assert inputs["reference_image_hardcoded"] is False
    assert inputs["system_bound_to_single_reference"] is False
