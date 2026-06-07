from __future__ import annotations

from pathlib import Path
from statistics import pvariance
from typing import Any

from PIL import Image, ImageStat

from avatar_engine.pipeline.stages.base import sha256_file


ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def validate_image(path: Path, *, expected_width: int, expected_height: int, min_variance: float = 1.0) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
        "extension_valid": path.suffix.lower() in ALLOWED_EXTENSIONS,
        "size_bytes": path.stat().st_size if path.exists() else 0,
        "file_valid": False,
        "width": 0,
        "height": 0,
        "dimensions_valid": False,
        "sha256": "",
        "non_blank": False,
        "variance": 0.0,
        "technical_validation": "failed",
        "visual_acceptance": "pending",
    }
    if not result["exists"] or not result["extension_valid"] or result["size_bytes"] <= 0:
        return result
    try:
        with Image.open(path) as image:
            image.load()
            result["width"], result["height"] = image.size
            result["file_valid"] = True
            result["dimensions_valid"] = image.size == (expected_width, expected_height)
            rgb = image.convert("RGB")
            stat = ImageStat.Stat(rgb)
            extrema = rgb.getextrema()
            channel_variance = pvariance(stat.mean) + sum(stat.var)
            result["variance"] = float(channel_variance)
            all_black = all(high == 0 for _low, high in extrema)
            all_white = all(low == 255 for low, _high in extrema)
            result["non_blank"] = not all_black and not all_white and channel_variance > min_variance
    except Exception as exc:
        result["error"] = str(exc)
        return result
    result["sha256"] = sha256_file(path)
    if result["file_valid"] and result["dimensions_valid"] and result["non_blank"]:
        result["technical_validation"] = "passed"
    return result
