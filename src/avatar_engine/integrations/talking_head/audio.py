from __future__ import annotations

import json
import base64
import shutil
import subprocess
import wave
from pathlib import Path
from typing import Any

from avatar_engine.pipeline.stages.base import sha256_file


def synthesize_text_with_sapi(text: str, output_path: Path) -> dict[str, Any]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    escaped_output = str(output_path).replace("'", "''")
    escaped_text = text.replace("'", "''")
    script = (
        "Add-Type -AssemblyName System.Speech; "
        "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        f"$s.SetOutputToWaveFile('{escaped_output}'); "
        f"$s.Speak('{escaped_text}'); "
        "$s.Dispose();"
    )
    encoded_script = base64.b64encode(script.encode("utf-16le")).decode("ascii")
    completed = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-EncodedCommand", encoded_script],
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    return {
        "adapter": "windows_sapi",
        "command": ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-EncodedCommand", "System.Speech.Synthesis.SpeechSynthesizer"],
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "output_path": str(output_path),
        "succeeded": completed.returncode == 0 and output_path.exists() and output_path.stat().st_size > 0,
    }


def write_test_tone(path: Path, duration_seconds: float = 3.2, sample_rate: int = 16000) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame_count = int(duration_seconds * sample_rate)
    amplitude = 8000
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        frames = bytearray()
        for index in range(frame_count):
            sample = int(amplitude if (index // 80) % 2 == 0 else -amplitude)
            frames.extend(sample.to_bytes(2, byteorder="little", signed=True))
        handle.writeframes(bytes(frames))


def transliterate_cyrillic(text: str) -> str:
    table = str.maketrans(
        {
            "А": "A",
            "Б": "B",
            "В": "V",
            "Г": "G",
            "Д": "D",
            "Е": "E",
            "Ё": "Yo",
            "Ж": "Zh",
            "З": "Z",
            "И": "I",
            "Й": "Y",
            "К": "K",
            "Л": "L",
            "М": "M",
            "Н": "N",
            "О": "O",
            "П": "P",
            "Р": "R",
            "С": "S",
            "Т": "T",
            "У": "U",
            "Ф": "F",
            "Х": "Kh",
            "Ц": "Ts",
            "Ч": "Ch",
            "Ш": "Sh",
            "Щ": "Shch",
            "Ъ": "",
            "Ы": "Y",
            "Ь": "",
            "Э": "E",
            "Ю": "Yu",
            "Я": "Ya",
            "а": "a",
            "б": "b",
            "в": "v",
            "г": "g",
            "д": "d",
            "е": "e",
            "ё": "yo",
            "ж": "zh",
            "з": "z",
            "и": "i",
            "й": "y",
            "к": "k",
            "л": "l",
            "м": "m",
            "н": "n",
            "о": "o",
            "п": "p",
            "р": "r",
            "с": "s",
            "т": "t",
            "у": "u",
            "ф": "f",
            "х": "kh",
            "ц": "ts",
            "ч": "ch",
            "ш": "sh",
            "щ": "shch",
            "ъ": "",
            "ы": "y",
            "ь": "",
            "э": "e",
            "ю": "yu",
            "я": "ya",
        }
    )
    return text.translate(table)


def probe_audio(path: Path, ffprobe_path: str = "ffprobe") -> dict[str, Any]:
    if shutil.which(ffprobe_path) is None:
        return {"ffprobe_available": False, "file_exists": path.exists(), "audio_stream_present": False}
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
        check=False,
        timeout=30,
    )
    payload: dict[str, Any] = {
        "ffprobe_available": True,
        "file_exists": path.exists(),
        "returncode": completed.returncode,
        "stderr": completed.stderr,
        "audio_stream_present": False,
    }
    if completed.returncode != 0:
        return payload
    details = json.loads(completed.stdout or "{}")
    audio_streams = [stream for stream in details.get("streams", []) if stream.get("codec_type") == "audio"]
    duration = float(details.get("format", {}).get("duration") or 0)
    stream = audio_streams[0] if audio_streams else {}
    payload.update(
        {
            "audio_stream_present": bool(audio_streams),
            "duration_seconds": duration,
            "sample_rate": int(stream.get("sample_rate") or 0),
            "channels": int(stream.get("channels") or 0),
            "format": details.get("format", {}).get("format_name", ""),
        }
    )
    return payload


def normalize_audio(input_path: Path, output_path: Path, ffmpeg_path: str = "ffmpeg") -> dict[str, Any]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        ffmpeg_path,
        "-y",
        "-i",
        str(input_path),
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-c:a",
        "pcm_s16le",
        str(output_path),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False, timeout=60)
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "output_path": str(output_path),
        "succeeded": completed.returncode == 0 and output_path.exists() and output_path.stat().st_size > 0,
    }


def validate_audio(path: Path, ffprobe_path: str = "ffprobe") -> dict[str, Any]:
    probe = probe_audio(path, ffprobe_path)
    result = {
        "input_path": str(path),
        "file_exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else 0,
        "sha256": sha256_file(path) if path.exists() else "",
        **probe,
    }
    duration = float(result.get("duration_seconds") or 0)
    result["duration_in_allowed_range"] = 3 <= duration <= 15
    result["audio_valid"] = bool(
        result["file_exists"]
        and result["size_bytes"] > 0
        and result.get("audio_stream_present")
        and result["duration_in_allowed_range"]
        and int(result.get("sample_rate") or 0) > 0
    )
    return result
