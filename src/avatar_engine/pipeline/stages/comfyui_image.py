from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from avatar_engine.integrations.comfyui.client import HttpComfyUIClient
from avatar_engine.integrations.comfyui.generation_limit import GenerationCounters
from avatar_engine.integrations.comfyui.image_validation import validate_image
from avatar_engine.integrations.comfyui.interface import ComfyUIClient
from avatar_engine.integrations.comfyui.preflight import build_preflight_report
from avatar_engine.integrations.comfyui.workflow_loader import get_checkpoint_name, load_workflow
from avatar_engine.integrations.comfyui.workflow_patcher import patch_controlled_inputs
from avatar_engine.jobs.repository import utc_now
from avatar_engine.models import Artifact
from avatar_engine.pipeline.context import PipelineContext
from avatar_engine.pipeline.stages.base import StageResult, sha256_file


DEFAULT_PROMPT = (
    "portrait of a fictional adult digital presenter, front-facing, neutral expression, "
    "simple studio background, soft lighting, realistic skin, clear eyes, high detail"
)
DEFAULT_NEGATIVE_PROMPT = (
    "deformed face, extra eyes, extra mouth, duplicate face, bad anatomy, blurry, low quality, text, watermark"
)


def comfyui_image_stage_names() -> list[str]:
    return [stage.name for stage in comfyui_image_stages()]


def comfyui_image_stages(client: ComfyUIClient | None = None) -> list[Any]:
    return [
        ValidateComfyUIImageInputsStage(),
        ComfyUIPreflightStage(client),
        LoadComfyUIWorkflowStage(),
        PatchComfyUIWorkflowStage(),
        SubmitComfyUIWorkflowStage(client),
        ValidateComfyUIImageOutputStage(),
        BuildComfyUIImageManifestStage(),
    ]


class ValidateComfyUIImageInputsStage:
    name = "validate_inputs"
    uses_gpu = False

    def run(self, context: PipelineContext) -> StageResult:
        job = context.metadata["job"]
        inputs = normalized_inputs(job.input_json, context.project_root)
        errors: list[str] = []
        if inputs["mode"] != "comfyui_image":
            errors.append("mode must be comfyui_image")
        if inputs["images_requested"] != 1 or inputs["batch_size"] != 1:
            errors.append("images_requested and batch_size must both be 1")
        if inputs["max_generations"] != 1:
            errors.append("max_generations must be 1")
        if inputs["automatic_retry"] is not False:
            errors.append("automatic_retry must be false")
        if inputs["width"] <= 0 or inputs["height"] <= 0:
            errors.append("width and height must be positive")
        if inputs["steps"] <= 0:
            errors.append("steps must be positive")
        if not inputs["workflow_path"].exists():
            errors.append(f"workflow does not exist: {inputs['workflow_path']}")

        job_json = {
            "job_id": context.job_id,
            "created_at": job.created_at,
            "status": job.status,
            "input": {key: str(value) if isinstance(value, Path) else value for key, value in inputs.items()},
        }
        write_json(context.job_dir / "job.json", job_json)
        context.metadata["comfyui_inputs"] = inputs
        if errors:
            return StageResult(status="failed", error_message="; ".join(errors), stderr="\n".join(errors))
        return StageResult(stdout="comfyui image inputs validated")


class ComfyUIPreflightStage:
    name = "comfyui_preflight"
    uses_gpu = False

    def __init__(self, client: ComfyUIClient | None = None):
        self.client = client

    def run(self, context: PipelineContext) -> StageResult:
        inputs = context.metadata["comfyui_inputs"]
        client = self.client or HttpComfyUIClient(context.config.comfyui_base_url)
        preflight_dir = context.job_dir / "preflight"
        health = client.health()
        report: dict[str, Any] = {
            "comfyui_reachable": health.available,
            "base_url": context.config.comfyui_base_url,
            "system_stats_received": False,
            "object_info_received": False,
            "submit_allowed": False,
            "real_generation_executed": False,
        }
        if not health.available:
            write_json(preflight_dir / "comfyui_preflight.json", report)
            return StageResult(status="failed", error_message="ComfyUI is not reachable", stderr=json.dumps(report))

        system_stats = client.get_system_stats()
        object_info = client.get_object_info()
        report.update(
            {
                "system_stats_received": system_stats.received,
                "object_info_received": object_info.received,
            }
        )
        report.update(
            build_preflight_report(
                workflow_path=inputs["workflow_path"],
                object_info=object_info.details,
                comfyui_root=context.config.comfyui_root,
            )
        )
        write_json(preflight_dir / "comfyui_preflight.json", report)
        context.metadata["comfyui_preflight"] = report
        context.metadata["comfyui_object_info"] = object_info.details
        if not report["submit_allowed"]:
            return StageResult(status="failed", error_message="ComfyUI preflight blocked submit", stderr=json.dumps(report))
        return StageResult(stdout="comfyui preflight passed")


class LoadComfyUIWorkflowStage:
    name = "load_workflow"
    uses_gpu = False

    def run(self, context: PipelineContext) -> StageResult:
        inputs = context.metadata["comfyui_inputs"]
        workflow = load_workflow(inputs["workflow_path"])
        workflow_dir = context.job_dir / "workflow"
        source_path = workflow_dir / "source_workflow.json"
        write_json(source_path, workflow)
        context.metadata["source_workflow"] = workflow
        context.metadata["workflow_source_snapshot"] = str(source_path)
        return StageResult(
            artifacts=[artifact_for(source_path, "source_workflow", self.name)],
            stdout="workflow loaded",
        )


class PatchComfyUIWorkflowStage:
    name = "patch_workflow"
    uses_gpu = False

    def run(self, context: PipelineContext) -> StageResult:
        inputs = context.metadata["comfyui_inputs"]
        workflow = context.metadata["source_workflow"]
        output_prefix = f"avatar_engine/{context.job_id}"
        patched, report = patch_controlled_inputs(
            workflow,
            checkpoint=inputs["checkpoint"],
            positive_prompt=inputs["prompt"],
            negative_prompt=inputs["negative_prompt"],
            seed=inputs["seed"],
            width=inputs["width"],
            height=inputs["height"],
            steps=inputs["steps"],
            cfg=inputs["cfg"],
            output_prefix=output_prefix,
            sampler=inputs["sampler"],
            scheduler=inputs["scheduler"],
        )
        workflow_dir = context.job_dir / "workflow"
        patched_path = workflow_dir / "patched_workflow.json"
        report_path = workflow_dir / "patch_report.json"
        write_json(patched_path, patched)
        write_json(report_path, report.to_dict())
        context.metadata["patched_workflow"] = patched
        context.metadata["patch_report"] = report.to_dict()
        context.metadata["output_prefix"] = output_prefix
        if report.missing_targets:
            return StageResult(status="failed", error_message="Workflow patch target missing", stderr=json.dumps(report.to_dict()))
        return StageResult(
            artifacts=[
                artifact_for(patched_path, "patched_workflow", self.name),
                artifact_for(report_path, "patch_report", self.name),
            ],
            stdout="workflow patched",
        )


class SubmitComfyUIWorkflowStage:
    name = "submit_comfyui_workflow"
    uses_gpu = True

    def __init__(self, client: ComfyUIClient | None = None):
        self.client = client

    def run(self, context: PipelineContext) -> StageResult:
        inputs = context.metadata["comfyui_inputs"]
        client = self.client or HttpComfyUIClient(context.config.comfyui_base_url, timeout=30.0)
        counters = GenerationCounters(max_generations=1)
        counters.before_submit()
        counters.mark_submit_attempt()
        submit = client.submit_workflow(context.metadata["patched_workflow"])
        counters.mark_successful_submit()
        submit_log = {
            "prompt_id": submit.prompt_id,
            "submitted": submit.submitted,
            "details": submit.details,
            **counters.to_dict(),
            "automatic_retry_executed": False,
        }
        write_json(context.logs_dir / "comfyui_submit.json", submit_log)

        history = client.wait_for_completion(
            submit.prompt_id,
            timeout_seconds=inputs["timeout_seconds"],
            poll_interval=inputs["poll_interval"],
        )
        write_json(context.logs_dir / "comfyui_history.json", {"prompt_id": submit.prompt_id, "status": history.status, "details": history.details})
        if history.status != "completed":
            context.metadata["generation_counters"] = counters.to_dict()
            context.metadata["prompt_id"] = submit.prompt_id
            return StageResult(status="failed", error_message=f"ComfyUI prompt ended with status {history.status}", stderr=json.dumps(history.details))

        outputs = client.collect_outputs(submit.prompt_id)
        if len(outputs) != 1:
            return StageResult(status="failed", error_message=f"Expected exactly one ComfyUI image output, got {len(outputs)}")
        output = outputs[0]
        destination = context.output_dir / output.filename
        if hasattr(client, "download_output"):
            client.download_output(output, destination)  # type: ignore[attr-defined]
        else:
            raise RuntimeError("ComfyUI client cannot download real output")
        image_artifact = artifact_for(destination, "generated_image", self.name)
        context.metadata.update(
            {
                "prompt_id": submit.prompt_id,
                "history_status": history.status,
                "generated_image_path": str(destination),
                "generation_counters": counters.to_dict(),
                "real_generation_executed": True,
                "gpu_lock_acquired": True,
            }
        )
        return StageResult(
            artifacts=[image_artifact],
            metadata={
                "prompt_id": submit.prompt_id,
                "generated_image_path": str(destination),
                "generation_counters": counters.to_dict(),
                "real_generation_executed": True,
                "gpu_lock_acquired": True,
            },
            stdout=f"downloaded {destination}",
        )


class ValidateComfyUIImageOutputStage:
    name = "validate_image"
    uses_gpu = False

    def run(self, context: PipelineContext) -> StageResult:
        inputs = context.metadata["comfyui_inputs"]
        image_path = Path(context.metadata["generated_image_path"])
        validation = validate_image(image_path, expected_width=inputs["width"], expected_height=inputs["height"])
        path = context.job_dir / "image_validation.json"
        write_json(path, validation)
        context.metadata["image_validation"] = validation
        if validation["technical_validation"] != "passed":
            return StageResult(status="failed", error_message="Generated image failed technical validation", stderr=json.dumps(validation))
        return StageResult(
            artifacts=[artifact_for(path, "image_validation", self.name)],
            metadata={"image_sha256": validation["sha256"], "image_width": validation["width"], "image_height": validation["height"]},
            stdout="image technical validation passed",
        )


class BuildComfyUIImageManifestStage:
    name = "build_manifest"
    uses_gpu = False

    def run(self, context: PipelineContext) -> StageResult:
        inputs = context.metadata["comfyui_inputs"]
        validation = context.metadata["image_validation"]
        counters = context.metadata["generation_counters"]
        image_path = context.metadata["generated_image_path"]
        finished_at = utc_now()
        manifest = {
            "job_id": context.job_id,
            "mode": "comfyui_image",
            "comfyui_base_url": context.config.comfyui_base_url,
            "workflow_source": str(inputs["workflow_path"]),
            "checkpoint": inputs["checkpoint"],
            "seed": inputs["seed"],
            "width": inputs["width"],
            "height": inputs["height"],
            "steps": inputs["steps"],
            "cfg": inputs["cfg"],
            "prompt_id": context.metadata["prompt_id"],
            "submit_attempts": counters["submit_attempts"],
            "successful_submits": counters["successful_submits"],
            "generation_attempts": counters["generation_attempts"],
            "max_generations": counters["max_generations"],
            "automatic_retry_executed": False,
            "output_images": [image_path],
            "technical_result": validation["technical_validation"],
            "operator_visual_review": "pending",
            "production_accepted": False,
            "finished_at": finished_at,
        }
        review_packet = {
            "job_id": context.job_id,
            "image_path": image_path,
            "prompt": inputs["prompt"],
            "negative_prompt": inputs["negative_prompt"],
            "checkpoint": inputs["checkpoint"],
            "seed": inputs["seed"],
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
            artifacts=[
                artifact_for(manifest_path, "manifest", self.name),
                artifact_for(review_path, "operator_review_packet", self.name),
            ],
            metadata={"manifest_path": str(manifest_path), "operator_review_packet_path": str(review_path)},
            stdout="comfyui image manifest built",
        )


def normalized_inputs(input_json: dict[str, Any], project_root: Path) -> dict[str, Any]:
    workflow_value = input_json.get("workflow", "workflows/simple_portrait.json")
    workflow_path = Path(str(workflow_value))
    if not workflow_path.is_absolute():
        workflow_path = project_root / workflow_path
    checkpoint = str(input_json.get("checkpoint") or "")
    if not checkpoint:
        try:
            checkpoint = get_checkpoint_name(load_workflow(workflow_path))
        except Exception:
            checkpoint = ""
    return {
        "mode": input_json.get("mode", "comfyui_image"),
        "workflow_path": workflow_path,
        "prompt": input_json.get("prompt") or DEFAULT_PROMPT,
        "negative_prompt": input_json.get("negative_prompt") or DEFAULT_NEGATIVE_PROMPT,
        "checkpoint": checkpoint,
        "seed": int(input_json.get("seed", 20260607)),
        "width": int(input_json.get("width", 512)),
        "height": int(input_json.get("height", 512)),
        "steps": int(input_json.get("steps", 15)),
        "cfg": float(input_json.get("cfg", 6.5)),
        "sampler": str(input_json.get("sampler", "euler")),
        "scheduler": str(input_json.get("scheduler", "normal")),
        "batch_size": int(input_json.get("batch_size", 1)),
        "images_requested": int(input_json.get("images_requested", 1)),
        "max_generations": int(input_json.get("max_generations", 1)),
        "automatic_retry": bool(input_json.get("automatic_retry", False)),
        "timeout_seconds": float(input_json.get("timeout_seconds", 900)),
        "poll_interval": float(input_json.get("poll_interval", 2)),
    }


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
