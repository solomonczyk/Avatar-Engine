from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from avatar_engine.integrations.talking_head.attempts import TalkingHeadAttemptCounters
from avatar_engine.integrations.talking_head.audio import (
    normalize_audio,
    synthesize_text_with_sapi,
    transliterate_cyrillic,
    validate_audio,
)
from avatar_engine.integrations.talking_head.reference_image import copy_reference_to_job, validate_reference_image
from avatar_engine.integrations.talking_head.runtime import (
    TalkingHeadSettings,
    discover_runtime_candidates,
    runtime_from_selection,
    write_command_log,
)
from avatar_engine.integrations.talking_head.video_validation import create_preview_artifacts, validate_video
from avatar_engine.jobs.repository import utc_now
from avatar_engine.models import Artifact
from avatar_engine.pipeline.context import PipelineContext
from avatar_engine.pipeline.stages.base import StageResult, sha256_file


DEFAULT_TALKING_HEAD_TEXT = "Здравствуйте. Это первая проверка работы локального говорящего аватара."


def talking_head_stage_names() -> list[str]:
    return [stage.name for stage in talking_head_stages()]


def talking_head_stages() -> list[Any]:
    return [
        ValidateReferenceImageStage(),
        PrepareJobReferenceCopyStage(),
        PrepareAudioStage(),
        SelectTalkingHeadRuntimeStage(),
        RuntimePreflightStage(),
        ExecuteTalkingHeadOnceStage(),
        CollectVideoStage(),
        ValidateTalkingHeadVideoStage(),
        CreatePreviewArtifactsStage(),
        BuildTalkingHeadManifestStage(),
    ]


class ValidateReferenceImageStage:
    name = "validate_reference_image"
    uses_gpu = False

    def run(self, context: PipelineContext) -> StageResult:
        job = context.metadata["job"]
        inputs = normalize_talking_head_inputs(job.input_json, context.project_root)
        errors: list[str] = []
        if inputs["mode"] != "talking_head":
            errors.append("mode must be talking_head")
        if inputs["reference_image_path"] is None:
            errors.append("reference_image_path is required")
        if inputs["audio_path"] is None and not inputs["text"]:
            errors.append("exactly one of audio_path or text is required")
        if inputs["audio_path"] is not None and inputs["text"]:
            errors.append("audio_path and text are mutually exclusive")
        if inputs["max_talking_head_generations"] != 1:
            errors.append("max_talking_head_generations must be 1")
        if inputs["automatic_retry_enabled"] is not False:
            errors.append("automatic_retry_enabled must be false")

        reference_validation: dict[str, Any] = {}
        if inputs["reference_image_path"] is not None:
            reference_validation = validate_reference_image(inputs["reference_image_path"])
            if not reference_validation["reference_valid"]:
                errors.append("reference image failed technical validation")

        job_json = {
            "job_id": context.job_id,
            "created_at": job.created_at,
            "status": job.status,
            "input": stringify_paths(inputs),
            "reference_image_is_job_parameter": True,
            "reference_image_mode": "job_input",
            "reference_image_hardcoded": False,
            "system_bound_to_single_reference": False,
            "talking_head_attempts": 0,
            "max_talking_head_generations": 1,
            "automatic_retry_enabled": False,
        }
        write_json(context.job_dir / "job.json", job_json)
        preflight_path = context.job_dir / "preflight" / "reference_image_validation.json"
        write_json(preflight_path, reference_validation)
        context.metadata["talking_head_inputs"] = inputs
        context.metadata["reference_image_validation"] = reference_validation
        if errors:
            return StageResult(status="failed", error_message="; ".join(errors), stderr="\n".join(errors))
        return StageResult(
            artifacts=[artifact_for(preflight_path, "reference_image_validation", self.name)],
            stdout="reference image input validated",
        )


class PrepareJobReferenceCopyStage:
    name = "prepare_job_reference_copy"
    uses_gpu = False

    def run(self, context: PipelineContext) -> StageResult:
        inputs = context.metadata["talking_head_inputs"]
        source = inputs["reference_image_path"]
        destination = copy_reference_to_job(source, context.input_dir / "reference")
        validation = context.metadata["reference_image_validation"]
        validation.update(
            {
                "copied_to_job_input": True,
                "job_reference_copy": str(destination),
                "original_filename": source.name,
                "reference_original_not_modified": sha256_file(source) == validation["sha256"],
            }
        )
        path = context.job_dir / "preflight" / "reference_image_validation.json"
        write_json(path, validation)
        return StageResult(
            artifacts=[artifact_for(destination, "job_reference_image", self.name)],
            metadata={"job_reference_image_path": str(destination), "reference_image_sha256": validation["sha256"]},
            stdout="reference image copied into job input",
        )


class PrepareAudioStage:
    name = "prepare_audio"
    uses_gpu = False

    def run(self, context: PipelineContext) -> StageResult:
        inputs = context.metadata["talking_head_inputs"]
        audio_dir = context.input_dir / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)
        source_path: Path
        audio_source = "file"
        tts_report: dict[str, Any] | None = None
        if inputs["audio_path"] is not None:
            source_path = audio_dir / f"source_audio{inputs['audio_path'].suffix.lower()}"
            shutil.copy2(inputs["audio_path"], source_path)
        else:
            audio_source = "text"
            source_path = audio_dir / "sapi_text_source.wav"
            tts_report = synthesize_text_with_sapi(inputs["text"], source_path)
            if not tts_report["succeeded"]:
                path = context.job_dir / "preflight" / "audio_validation.json"
                write_json(path, {"audio_source": audio_source, "tts_report": tts_report, "audio_valid": False})
                return StageResult(status="failed", error_message="Local TTS failed", stderr=json.dumps(tts_report))

        normalized_path = audio_dir / "audio_16khz_mono.wav"
        normalize_report = normalize_audio(source_path, normalized_path, context.config.ffmpeg_path)
        if not normalize_report["succeeded"]:
            path = context.job_dir / "preflight" / "audio_validation.json"
            write_json(path, {"audio_source": audio_source, "normalize_report": normalize_report, "audio_valid": False})
            return StageResult(status="failed", error_message="Audio normalization failed", stderr=json.dumps(normalize_report))

        validation = validate_audio(normalized_path)
        if audio_source == "text" and not validation["audio_valid"]:
            transliterated = transliterate_cyrillic(inputs["text"])
            if transliterated != inputs["text"]:
                source_path = audio_dir / "sapi_text_source_transliterated.wav"
                tts_report = synthesize_text_with_sapi(transliterated, source_path)
                if tts_report["succeeded"]:
                    normalize_report = normalize_audio(source_path, normalized_path, context.config.ffmpeg_path)
                    validation = validate_audio(normalized_path)
                    validation["text_transliteration_used"] = True
                    validation["transliterated_text"] = transliterated
        validation.update(
            {
                "audio_source": audio_source,
                "source_audio_path": str(source_path),
                "normalized_audio_path": str(normalized_path),
                "tts_report": tts_report,
                "normalize_report": normalize_report,
            }
        )
        path = context.job_dir / "preflight" / "audio_validation.json"
        write_json(path, validation)
        if not validation["audio_valid"]:
            return StageResult(status="failed", error_message="Audio failed validation", stderr=json.dumps(validation))
        return StageResult(
            artifacts=[artifact_for(normalized_path, "job_audio", self.name), artifact_for(path, "audio_validation", self.name)],
            metadata={
                "audio_source": audio_source,
                "audio_path": str(normalized_path),
                "audio_sha256": validation["sha256"],
                "audio_duration_seconds": validation["duration_seconds"],
            },
            stdout="audio prepared and validated",
        )


class SelectTalkingHeadRuntimeStage:
    name = "select_talking_head_runtime"
    uses_gpu = False

    def run(self, context: PipelineContext) -> StageResult:
        inputs = context.metadata["talking_head_inputs"]
        selection = discover_runtime_candidates(
            context.project_root,
            context.config.comfyui_root,
            allow_fake_runtime=inputs["allow_fake_runtime"],
        )
        selection.update(
            {
                "reference_image_mode": "job_input",
                "reference_image_hardcoded": False,
                "system_bound_to_single_reference": False,
                "gpu_worker_concurrency": context.config.gpu_worker_concurrency,
                "parallel_gpu_execution": False,
            }
        )
        path = context.job_dir / "preflight" / "talking_head_runtime_selection.json"
        write_json(path, selection)
        context.metadata["runtime_selection"] = selection
        if not selection["execution_allowed"]:
            blocker = {
                **selection,
                "talking_head_attempts": 0,
                "max_talking_head_generations": 1,
                "automatic_retry_executed": False,
            }
            return StageResult(status="failed", error_message=selection["next_allowed_action"], stderr=json.dumps(blocker))
        return StageResult(
            artifacts=[artifact_for(path, "talking_head_runtime_selection", self.name)],
            metadata={"selected_runtime": selection["selected_runtime"]},
            stdout=f"selected runtime {selection['selected_runtime']}",
        )


class RuntimePreflightStage:
    name = "runtime_preflight"
    uses_gpu = False

    def run(self, context: PipelineContext) -> StageResult:
        selection = context.metadata["runtime_selection"]
        runtime = runtime_from_selection(selection, context.config.ffmpeg_path)
        reference = Path(context.metadata["job_reference_image_path"])
        audio = Path(context.metadata["audio_path"])
        preflight = runtime.preflight(reference, audio)
        payload = {
            "runtime": runtime.name,
            "preflight_allowed": preflight.allowed,
            "details": preflight.details,
            "runtime_settings": TalkingHeadSettings().to_dict(),
        }
        path = context.job_dir / "preflight" / "talking_head_runtime_preflight.json"
        write_json(path, payload)
        context.metadata["runtime"] = runtime
        context.metadata["runtime_settings"] = TalkingHeadSettings()
        context.metadata["runtime_preflight"] = payload
        if not preflight.allowed:
            return StageResult(status="failed", error_message="Talking-head runtime preflight failed", stderr=json.dumps(payload))
        return StageResult(
            artifacts=[artifact_for(path, "talking_head_runtime_preflight", self.name)],
            stdout="talking-head runtime preflight passed",
        )


class ExecuteTalkingHeadOnceStage:
    name = "execute_talking_head_once"
    uses_gpu = True

    def run(self, context: PipelineContext) -> StageResult:
        runtime = context.metadata["runtime"]
        settings = context.metadata["runtime_settings"]
        counters = TalkingHeadAttemptCounters()
        counters.mark_started()
        reference = Path(context.metadata["job_reference_image_path"])
        audio = Path(context.metadata["audio_path"])
        work_dir = context.work_dir / "talking_head"
        result = runtime.generate(reference, audio, work_dir, settings)
        write_command_log(context.logs_dir / "runtime_command.json", result.command, runtime.name)
        (context.logs_dir / "runtime_stdout.log").write_text(result.stdout, encoding="utf-8")
        (context.logs_dir / "runtime_stderr.log").write_text(result.stderr, encoding="utf-8")
        metadata = {
            "talking_head_counters": counters.to_dict(),
            "runtime_command": result.command,
            "runtime_stdout_path": str(context.logs_dir / "runtime_stdout.log"),
            "runtime_stderr_path": str(context.logs_dir / "runtime_stderr.log"),
            "runtime_work_video_path": str(result.output_video),
            "real_talking_head_generation_executed": runtime.name != "fake_talking_head",
            "gpu_lock_acquired": True,
        }
        if result.returncode != 0 or not result.output_video.exists():
            return StageResult(status="failed", metadata=metadata, error_message="Talking-head subprocess failed", stderr=result.stderr)
        return StageResult(metadata=metadata, stdout="talking-head subprocess completed")


class CollectVideoStage:
    name = "collect_video"
    uses_gpu = False

    def run(self, context: PipelineContext) -> StageResult:
        source = Path(context.metadata["runtime_work_video_path"])
        output = context.output_dir / f"{context.job_id}_talking_head.mp4"
        shutil.copy2(source, output)
        return StageResult(
            artifacts=[artifact_for(output, "talking_head_video", self.name)],
            metadata={"output_video_path": str(output), "output_video_sha256": sha256_file(output)},
            stdout="talking-head video collected",
        )


class ValidateTalkingHeadVideoStage:
    name = "validate_video"
    uses_gpu = False

    def run(self, context: PipelineContext) -> StageResult:
        video_path = Path(context.metadata["output_video_path"])
        validation = validate_video(
            video_path,
            expected_audio_duration=float(context.metadata.get("audio_duration_seconds") or 0),
            ffmpeg_path=context.config.ffmpeg_path,
        )
        path = context.job_dir / "video_validation.json"
        write_json(path, validation)
        if validation["technical_validation"] != "passed":
            return StageResult(status="failed", error_message="Video failed technical validation", stderr=json.dumps(validation))
        return StageResult(
            artifacts=[artifact_for(path, "video_validation", self.name)],
            metadata={
                "video_validation": validation,
                "video_duration_seconds": validation["duration_seconds"],
                "video_width": validation["width"],
                "video_height": validation["height"],
            },
            stdout="talking-head video technical validation passed",
        )


class CreatePreviewArtifactsStage:
    name = "create_preview_artifacts"
    uses_gpu = False

    def run(self, context: PipelineContext) -> StageResult:
        preview_paths = create_preview_artifacts(Path(context.metadata["output_video_path"]), context.job_dir / "preview", context.config.ffmpeg_path)
        artifacts = [artifact_for(Path(path), f"preview_{name}", self.name) for name, path in preview_paths.items()]
        return StageResult(artifacts=artifacts, metadata={"preview_artifacts": preview_paths}, stdout="preview artifacts created")


class BuildTalkingHeadManifestStage:
    name = "build_manifest"
    uses_gpu = False

    def run(self, context: PipelineContext) -> StageResult:
        inputs = context.metadata["talking_head_inputs"]
        validation = context.metadata["video_validation"]
        counters = context.metadata["talking_head_counters"]
        output_video = context.metadata["output_video_path"]
        manifest = {
            "job_id": context.job_id,
            "mode": "talking_head",
            "reference_image_mode": "job_input",
            "reference_image_original_path": str(inputs["reference_image_path"]),
            "reference_image_job_copy": context.metadata["job_reference_image_path"],
            "reference_image_sha256": context.metadata["reference_image_sha256"],
            "reference_image_hardcoded": False,
            "system_bound_to_single_reference": False,
            "audio_source": context.metadata["audio_source"],
            "audio_path": context.metadata["audio_path"],
            "audio_sha256": context.metadata["audio_sha256"],
            "runtime": context.metadata["selected_runtime"],
            "runtime_settings": context.metadata["runtime_settings"].to_dict(),
            **counters,
            "automatic_retry_executed": False,
            "new_face_generated": False,
            "face_swap_executed": False,
            "output_video": output_video,
            "output_video_sha256": context.metadata["output_video_sha256"],
            "technical_result": validation["technical_validation"],
            "operator_visual_review": "pending",
            "operator_visual_review_required": True,
            "production_accepted": False,
            "finished_at": utc_now(),
        }
        review_packet = {
            "job_id": context.job_id,
            "mode": "talking_head",
            "reference_image_path": context.metadata["job_reference_image_path"],
            "reference_image_sha256": context.metadata["reference_image_sha256"],
            "reference_image_mode": "job_input",
            "reference_image_hardcoded": False,
            "system_bound_to_single_reference": False,
            "audio_path": context.metadata["audio_path"],
            "audio_sha256": context.metadata["audio_sha256"],
            "runtime": context.metadata["selected_runtime"],
            "output_video_path": output_video,
            "output_video_sha256": context.metadata["output_video_sha256"],
            "technical_validation": validation["technical_validation"],
            "operator_visual_review_required": True,
            "operator_decision": "pending",
            "production_accepted": False,
        }
        manifest_path = context.job_dir / "manifest.json"
        review_path = context.job_dir / "operator_review_packet.json"
        write_json(manifest_path, manifest)
        write_json(review_path, review_packet)
        return StageResult(
            artifacts=[artifact_for(manifest_path, "manifest", self.name), artifact_for(review_path, "operator_review_packet", self.name)],
            metadata={"manifest_path": str(manifest_path), "operator_review_packet_path": str(review_path)},
            stdout="talking-head manifest built",
        )


def normalize_talking_head_inputs(input_json: dict[str, Any], project_root: Path) -> dict[str, Any]:
    reference_value = input_json.get("reference_image_path") or input_json.get("reference_image")
    audio_value = input_json.get("audio_path") or input_json.get("audio")
    reference_path = resolve_optional_path(reference_value, project_root)
    audio_path = resolve_optional_path(audio_value, project_root)
    return {
        "mode": str(input_json.get("mode", "talking_head")).replace("-", "_"),
        "reference_image_path": reference_path,
        "audio_path": audio_path,
        "text": input_json.get("text") or "",
        "reference_image_mode": "job_input",
        "reference_image_hardcoded": False,
        "system_bound_to_single_reference": False,
        "max_talking_head_generations": int(input_json.get("max_talking_head_generations", 1)),
        "automatic_retry_enabled": bool(input_json.get("automatic_retry_enabled", False)),
        "allow_fake_runtime": bool(input_json.get("allow_fake_runtime", False)),
    }


def resolve_optional_path(value: object, project_root: Path) -> Path | None:
    if value is None or str(value) == "":
        return None
    path = Path(str(value))
    return path if path.is_absolute() else project_root / path


def stringify_paths(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: str(value) if isinstance(value, Path) else value for key, value in payload.items()}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def artifact_for(path: Path, artifact_type: str, stage_name: str) -> Artifact:
    return Artifact(
        artifact_type=artifact_type,
        path=path,
        sha256=sha256_file(path),
        size_bytes=path.stat().st_size,
        stage_name=stage_name,
    )
