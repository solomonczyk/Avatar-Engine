from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol


@dataclass(frozen=True)
class RuntimeHealth:
    available: bool
    details: dict[str, Any]


@dataclass(frozen=True)
class RuntimePreflight:
    allowed: bool
    details: dict[str, Any]


@dataclass(frozen=True)
class TalkingHeadSettings:
    size: int = 256
    preprocess: str = "crop"
    still_mode: bool = True
    expression_scale: float = 1.0
    pose_style: int = 0
    enhancer: str | None = None
    attempts: int = 1
    timeout_seconds: int = 900

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass(frozen=True)
class TalkingHeadResult:
    output_video: Path
    command: list[str]
    returncode: int
    stdout: str
    stderr: str


class TalkingHeadRuntime(Protocol):
    name: str

    def health(self) -> RuntimeHealth:
        ...

    def preflight(self, reference_image: Path, audio_path: Path) -> RuntimePreflight:
        ...

    def generate(
        self,
        reference_image: Path,
        audio_path: Path,
        output_dir: Path,
        settings: TalkingHeadSettings,
    ) -> TalkingHeadResult:
        ...


class FakeTalkingHeadRuntime:
    name = "fake_talking_head"

    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        self.ffmpeg_path = ffmpeg_path

    def health(self) -> RuntimeHealth:
        return RuntimeHealth(
            available=shutil.which(self.ffmpeg_path) is not None,
            details={"ffmpeg_available": shutil.which(self.ffmpeg_path) is not None},
        )

    def preflight(self, reference_image: Path, audio_path: Path) -> RuntimePreflight:
        health = self.health()
        return RuntimePreflight(
            allowed=health.available and reference_image.exists() and audio_path.exists(),
            details={
                **health.details,
                "reference_image_exists": reference_image.exists(),
                "audio_exists": audio_path.exists(),
                "fake_generation_only": True,
            },
        )

    def generate(
        self,
        reference_image: Path,
        audio_path: Path,
        output_dir: Path,
        settings: TalkingHeadSettings,
    ) -> TalkingHeadResult:
        output_dir.mkdir(parents=True, exist_ok=True)
        output_video = output_dir / "fake_talking_head.mp4"
        command = [
            self.ffmpeg_path,
            "-y",
            "-loop",
            "1",
            "-i",
            str(reference_image),
            "-i",
            str(audio_path),
            "-vf",
            f"scale={settings.size}:{settings.size}:force_original_aspect_ratio=decrease,"
            f"pad={settings.size}:{settings.size}:(ow-iw)/2:(oh-ih)/2,format=yuv420p,"
            f"zoompan=z='min(zoom+0.0005,1.02)':d=125:s={settings.size}x{settings.size}:fps=25",
            "-shortest",
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            str(output_video),
        ]
        completed = subprocess.run(command, capture_output=True, text=True, timeout=settings.timeout_seconds, check=False)
        return TalkingHeadResult(
            output_video=output_video,
            command=command,
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )


def discover_runtime_candidates(project_root: Path, comfyui_root: Path, allow_fake_runtime: bool = False) -> dict[str, Any]:
    candidates = []
    if allow_fake_runtime:
        candidates.append(
            {
                "runtime": "fake_talking_head",
                "code_available": True,
                "weights_available": True,
                "compatible_with_gpu": True,
                "license_compatible": True,
                "selected": True,
                "reason": "Explicit fake runtime for local tests; no model inference is performed.",
                "settings": TalkingHeadSettings().to_dict(),
            }
        )
        return {
            "candidates": candidates,
            "selected_runtime": "fake_talking_head",
            "model_download_required": False,
            "execution_allowed": True,
        }

    search_roots = [
        project_root.parent / "SadTalker",
        project_root.parent / "LivePortrait",
        project_root.parent / "MuseTalk",
        project_root.parent / "Wav2Lip",
        comfyui_root / "models",
        comfyui_root / "custom_nodes",
        comfyui_root / "comfyUI_portable_inst" / "ComfyUI" / "custom_nodes",
    ]
    runtime_names = [
        (
            "comfyui_talking_head_workflow",
            ["sadtalker", "livetalking", "liveportrait", "musetalk", "wav2lip", "talkinghead", "talking_head"],
            ["sadtalker", "liveportrait", "musetalk", "wav2lip", "talkinghead", "talking_head"],
        ),
        ("sadtalker", ["SadTalker", "sadtalker"], ["sadtalker", "auido2exp", "mapping_"]),
        ("liveportrait", ["LivePortrait", "liveportrait"], ["liveportrait"]),
        ("musetalk", ["MuseTalk", "musetalk"], ["musetalk"]),
        ("wav2lip", ["Wav2Lip", "wav2lip"], ["wav2lip"]),
    ]
    for runtime, code_needles, weight_needles in runtime_names:
        code_paths = find_matching_paths(search_roots, code_needles)
        weight_paths = find_matching_paths(search_roots, weight_needles)
        code_available = bool(code_paths)
        weights_available = bool(weight_paths)
        license_compatible = has_license_marker(code_paths)
        compatible = code_available and weights_available
        executable_adapter_available = False
        selected = compatible and license_compatible and executable_adapter_available
        candidates.append(
            {
                "runtime": runtime,
                "code_available": code_available,
                "weights_available": weights_available,
                "compatible_with_gpu": compatible,
                "license_compatible": license_compatible,
                "executable_adapter_available": executable_adapter_available,
                "selected": selected,
                "reason": runtime_reason(code_available, weights_available, license_compatible, executable_adapter_available),
                "code_paths": [str(path) for path in code_paths[:5]],
                "weight_paths": [str(path) for path in weight_paths[:5]],
            }
        )
        if selected:
            break

    selected_runtime = next((candidate["runtime"] for candidate in candidates if candidate["selected"]), "")
    return {
        "candidates": candidates,
        "selected_runtime": selected_runtime,
        "model_download_required": not bool(selected_runtime),
        "execution_allowed": bool(selected_runtime),
        "real_talking_head_generation_executed": False,
        "next_allowed_action": "" if selected_runtime else "talking_head_runtime_asset_authorization_required",
    }


def find_matching_paths(search_roots: list[Path], needles: list[str], max_depth: int = 5) -> list[Path]:
    matches: list[Path] = []
    lowered = [needle.lower() for needle in needles]
    for root in search_roots:
        if not root.exists():
            continue
        try:
            root_depth = len(root.parts)
            for child in root.rglob("*"):
                if len(child.parts) - root_depth > max_depth:
                    continue
                name = child.name.lower()
                if any(needle in name for needle in lowered):
                    matches.append(child)
                    if len(matches) >= 12:
                        return matches
        except (OSError, PermissionError):
            continue
    return matches


def has_license_marker(paths: list[Path]) -> bool:
    for path in paths:
        directory = path if path.is_dir() else path.parent
        for name in ["LICENSE", "LICENSE.txt", "license.md", "README.md"]:
            if (directory / name).exists():
                return True
    return False


def runtime_reason(
    code_available: bool,
    weights_available: bool,
    license_compatible: bool,
    executable_adapter_available: bool,
) -> str:
    if not code_available:
        return "Runtime code not found locally."
    if not weights_available:
        return "Runtime code found, but required weights were not found locally."
    if not license_compatible:
        return "Runtime assets found, but local personal-use license compatibility was not confirmed."
    if not executable_adapter_available:
        return "Runtime-like assets found, but no implemented local subprocess adapter is configured."
    return "Runtime appears locally available."


def runtime_from_selection(selection: dict[str, Any], ffmpeg_path: str = "ffmpeg") -> TalkingHeadRuntime:
    if selection.get("selected_runtime") == "fake_talking_head":
        return FakeTalkingHeadRuntime(ffmpeg_path)
    raise ValueError(f"No executable adapter is configured for runtime: {selection.get('selected_runtime')}")


def write_command_log(path: Path, command: list[str], runtime: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"runtime": runtime, "command": command}, indent=2, sort_keys=True),
        encoding="utf-8",
    )
