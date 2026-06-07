from avatar_engine.integrations.talking_head.reference_image import validate_reference_image


def test_reference_image_validation_accepts_supported_nonblank_image(sample_reference_image) -> None:
    result = validate_reference_image(sample_reference_image)

    assert result["file_exists"] is True
    assert result["format"] == "PNG"
    assert result["width"] > 0
    assert result["height"] > 0
    assert result["sha256"]
    assert result["reference_valid"] is True
