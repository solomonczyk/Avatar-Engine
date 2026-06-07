from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageStat

from avatar_engine.pipeline.stages.base import sha256_file


def probe_video(path: Path, ffprobe_path: str = "ffprobe") -> dict[str, Any]:
    if shutil.which(ffprobe_path) is None:
        return {"ffprobe_available": False, "file_exists": path.exists()}
    completed = subprocess.run(
        [
            ffprobe_path,
            "-v",
            "error",
            "-show_streams",
            "-show_format",
            "-print_format",
            "json",
            str(path),
        ],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    result: dict[str, Any] = {"ffprobe_available": True, "returncode": completed.returncode, "stderr": completed.stderr}
    if completed.returncode != 0:
        return result
    details = json.loads(completed.stdout or "{}")
    streams = details.get("streams", [])
    video_streams = [stream for stream in streams if stream.get("codec_type") == "video"]
    audio_streams = [stream for stream in streams if stream.get("codec_type") == "audio"]
    stream = video_streams[0] if video_streams else {}
    fps = parse_rate(stream.get("avg_frame_rate") or stream.get("r_frame_rate") or "0/1")
    duration = float(details.get("format", {}).get("duration") or stream.get("duration") or 0)
    frame_count = int(stream.get("nb_frames") or int(duration * fps) if fps else 0)
    result.update(
        {
            "video_stream_present": bool(video_streams),
            "audio_stream_present": bool(audio_streams),
            "duration_seconds": duration,
            "width": int(stream.get("width") or 0),
            "height": int(stream.get("height") or 0),
            "fps": fps,
            "frame_count": frame_count,
            "format": details.get("format", {}).get("format_name", ""),
        }
    )
    return result


def validate_video(path: Path, expected_audio_duration: float | None = None, ffmpeg_path: str = "ffmpeg", ffprobe_path: str = "ffprobe") -> dict[str, Any]:
    result: dict[str, Any] = {
        "file_valid": False,
        "file_exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else 0,
        "sha256": sha256_file(path) if path.exists() else "",
        "visual_acceptance": "pending",
    }
    result.update(probe_video(path, ffprobe_path))
    preview_dir = path.parent / "_validation_frames"
    frames = extract_validation_frames(path, preview_dir, ffmpeg_path, float(result.get("duration_seconds") or 0))
    result["first_last_frames_decoded"] = len(frames) >= 2
    result["black_frame_ratio"] = black_frame_ratio(frames)
    result["duplicate_frame_ratio"] = duplicate_frame_ratio(frames)
    duration = float(result.get("duration_seconds") or 0)
    duration_matches = True
    if expected_audio_duration:
        duration_matches = abs(duration - expected_audio_duration) <= max(1.0, expected_audio_duration * 0.35)
    result["duration_matches_audio"] = duration_matches
    result["technical_validation"] = "passed" if bool(
        result["file_exists"]
        and result["size_bytes"] > 0
        and result.get("video_stream_present")
        and result.get("audio_stream_present")
        and duration > 0
        and result.get("width", 0) > 0
        and result.get("height", 0) > 0
        and result.get("frame_count", 0) > 1
        and result.get("fps", 0) > 0
        and result["first_last_frames_decoded"]
        and result["black_frame_ratio"] < 1
        and duration_matches
    ) else "failed"
    result["file_valid"] = result["technical_validation"] == "passed"
    return result


def create_preview_artifacts(video_path: Path, preview_dir: Path, ffmpeg_path: str = "ffmpeg") -> dict[str, str]:
    preview_dir.mkdir(parents=True, exist_ok=True)
    probe = probe_video(video_path)
    duration = float(probe.get("duration_seconds") or 0)
    points = {
        "first_frame": 0,
        "middle_frame": max(duration / 2, 0),
        "last_frame": max(duration - 0.2, 0),
    }
    paths: dict[str, str] = {}
    for name, second in points.items():
        output = preview_dir / f"{name}.png"
        extract_frame(video_path, output, second, ffmpeg_path)
        paths[name] = str(output)
    contact_sheet = preview_dir / "contact_sheet.png"
    with Image.open(paths["first_frame"]) as first, Image.open(paths["middle_frame"]) as middle, Image.open(paths["last_frame"]) as last:
        frames = [first.convert("RGB"), middle.convert("RGB"), last.convert("RGB")]
        width = sum(frame.width for frame in frames)
        height = max(frame.height for frame in frames)
        sheet = Image.new("RGB", (width, height), "white")
        x = 0
        for frame in frames:
            sheet.paste(frame, (x, 0))
            x += frame.width
        sheet.save(contact_sheet)
    paths["contact_sheet"] = str(contact_sheet)
    return paths


def extract_validation_frames(video_path: Path, output_dir: Path, ffmpeg_path: str, duration: float) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    frames = []
    for index, second in enumerate([0, max(duration / 2, 0), max(duration - 0.2, 0)]):
        output = output_dir / f"frame_{index}.png"
        if extract_frame(video_path, output, second, ffmpeg_path):
            frames.append(output)
    return frames


def extract_frame(video_path: Path, output_path: Path, second: float, ffmpeg_path: str = "ffmpeg") -> bool:
    completed = subprocess.run(
        [ffmpeg_path, "-y", "-ss", f"{second:.3f}", "-i", str(video_path), "-frames:v", "1", str(output_path)],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    return completed.returncode == 0 and output_path.exists() and output_path.stat().st_size > 0


def black_frame_ratio(frames: list[Path]) -> float:
    if not frames:
        return 1.0
    black = 0
    for frame in frames:
        with Image.open(frame) as image:
            stat = ImageStat.Stat(image.convert("L"))
            if stat.mean[0] < 2:
                black += 1
    return black / len(frames)


def duplicate_frame_ratio(frames: list[Path]) -> float:
    if len(frames) < 2:
        return 1.0
    duplicates = 0
    comparisons = 0
    for left, right in zip(frames, frames[1:]):
        with Image.open(left) as left_image, Image.open(right) as right_image:
            diff = ImageChops.difference(left_image.convert("RGB"), right_image.convert("RGB"))
            stat = ImageStat.Stat(diff)
            comparisons += 1
            if sum(stat.mean) < 1:
                duplicates += 1
    return duplicates / comparisons if comparisons else 1.0


def parse_rate(value: str) -> float:
    if "/" not in value:
        return float(value or 0)
    numerator, denominator = value.split("/", 1)
    denominator_value = float(denominator or 1)
    return float(numerator or 0) / denominator_value if denominator_value else 0.0
