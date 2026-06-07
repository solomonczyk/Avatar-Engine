from pathlib import Path

from PIL import Image

from avatar_engine.integrations.comfyui.image_validation import validate_image


def test_valid_image_accepted_technically(tmp_path: Path) -> None:
    path = tmp_path / "valid.png"
    image = Image.new("RGB", (2, 2))
    image.putdata([(0, 0, 0), (255, 255, 255), (64, 128, 192), (192, 128, 64)])
    image.save(path)

    result = validate_image(path, expected_width=2, expected_height=2)

    assert result["technical_validation"] == "passed"
    assert result["visual_acceptance"] == "pending"
    assert result["sha256"]


def test_blank_image_rejected(tmp_path: Path) -> None:
    path = tmp_path / "blank.png"
    Image.new("RGB", (2, 2), "black").save(path)

    result = validate_image(path, expected_width=2, expected_height=2)

    assert result["technical_validation"] == "failed"
    assert result["non_blank"] is False
