from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from PIL import Image, ImageStat

from avatar_engine.pipeline.stages.base import sha256_file


ALLOWED_REFERENCE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def validate_reference_image(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "input_path": str(path),
        "file_exists": path.exists(),
        "allowed_extension": path.suffix.lower() in ALLOWED_REFERENCE_EXTENSIONS,
        "format": "",
        "width": 0,
        "height": 0,
        "sha256": "",
        "face_detection_executed": False,
        "face_detection_method": "not_available_without_optional_local_detector",
        "faces_detected": None,
        "face_sufficiently_large": None,
        "face_not_fully_occluded": None,
        "non_blank": False,
        "reference_valid": False,
        "copied_to_job_input": False,
    }
    if not result["file_exists"] or not result["allowed_extension"]:
        return result
    try:
        with Image.open(path) as image:
            image.load()
            result["format"] = image.format or ""
            result["width"], result["height"] = image.size
            rgb = image.convert("RGB")
            stat = ImageStat.Stat(rgb)
            result["non_blank"] = any(channel[1] > channel[0] for channel in stat.extrema)
    except Exception as exc:
        result["error"] = str(exc)
        return result

    result["sha256"] = sha256_file(path)
    result["reference_valid"] = bool(
        result["width"] > 0
        and result["height"] > 0
        and result["non_blank"]
        and result["allowed_extension"]
    )
    return result


def copy_reference_to_job(source: Path, reference_dir: Path) -> Path:
    reference_dir.mkdir(parents=True, exist_ok=True)
    destination = reference_dir / f"reference{source.suffix.lower()}"
    shutil.copy2(source, destination)
    return destination
