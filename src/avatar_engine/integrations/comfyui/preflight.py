from __future__ import annotations

from pathlib import Path
from typing import Any

from avatar_engine.integrations.comfyui.workflow_loader import (
    get_checkpoint_name,
    get_node_classes,
    has_save_image_node,
    load_workflow,
)


REQUIRED_NODE_CLASSES = [
    "CheckpointLoaderSimple",
    "CLIPTextEncode",
    "KSampler",
    "EmptyLatentImage",
    "VAEDecode",
    "SaveImage",
]


def build_preflight_report(
    *,
    workflow_path: Path,
    object_info: dict[str, Any],
    comfyui_root: Path,
) -> dict[str, Any]:
    workflow_valid = True
    workflow_error = ""
    try:
        workflow = load_workflow(workflow_path)
    except Exception as exc:
        workflow = {}
        workflow_valid = False
        workflow_error = str(exc)

    required_node_classes = get_node_classes(workflow) if workflow_valid else REQUIRED_NODE_CLASSES
    missing_node_classes = [class_name for class_name in required_node_classes if class_name not in object_info]
    checkpoint = get_checkpoint_name(workflow) if workflow_valid else ""
    available_checkpoints = available_checkpoint_names(object_info)
    checkpoint_available = checkpoint in available_checkpoints if checkpoint else False
    checkpoint_file_exists = checkpoint_path_exists(comfyui_root, checkpoint) if checkpoint else False
    save_image_present = has_save_image_node(workflow) if workflow_valid else False
    model_download_required = bool(checkpoint and not checkpoint_available)
    submit_allowed = (
        workflow_valid
        and bool(checkpoint)
        and checkpoint_available
        and checkpoint_file_exists
        and not missing_node_classes
        and save_image_present
        and not model_download_required
    )
    return {
        "checkpoint": checkpoint,
        "checkpoint_exists": checkpoint_available and checkpoint_file_exists,
        "checkpoint_available_in_comfyui": checkpoint_available,
        "checkpoint_file_exists": checkpoint_file_exists,
        "required_node_classes": required_node_classes,
        "missing_node_classes": missing_node_classes,
        "save_image_present": save_image_present,
        "workflow_valid": workflow_valid,
        "workflow_error": workflow_error,
        "model_download_required": model_download_required,
        "submit_allowed": submit_allowed,
        "real_generation_executed": False,
    }


def available_checkpoint_names(object_info: dict[str, Any]) -> list[str]:
    loader = object_info.get("CheckpointLoaderSimple", {})
    if not isinstance(loader, dict):
        return []
    required = loader.get("input", {}).get("required", {})
    if not isinstance(required, dict):
        return []
    ckpt_info = required.get("ckpt_name", [])
    if not isinstance(ckpt_info, list) or not ckpt_info:
        return []
    names = ckpt_info[0]
    return [name for name in names if isinstance(name, str)] if isinstance(names, list) else []


def checkpoint_path_exists(comfyui_root: Path, checkpoint: str) -> bool:
    if not checkpoint:
        return False
    if not comfyui_root.exists():
        return False
    for path in comfyui_root.rglob(checkpoint):
        if path.is_file():
            return True
    return False
