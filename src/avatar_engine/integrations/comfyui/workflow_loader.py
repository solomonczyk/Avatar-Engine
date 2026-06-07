from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_workflow(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("Workflow JSON must be an object")
    validate_workflow(data)
    return data


def validate_workflow(workflow: dict[str, Any]) -> None:
    if not workflow:
        raise ValueError("Workflow JSON must not be empty")
    for node_id, node in workflow.items():
        if not isinstance(node_id, str):
            raise ValueError("Workflow node IDs must be strings")
        if not isinstance(node, dict):
            raise ValueError(f"Workflow node {node_id} must be an object")
        if not isinstance(node.get("class_type"), str) or not node["class_type"]:
            raise ValueError(f"Workflow node {node_id} is missing class_type")
        if "inputs" in node and not isinstance(node.get("inputs"), dict):
            raise ValueError(f"Workflow node {node_id} is missing inputs")
    if has_unresolved_placeholders(workflow):
        raise ValueError("Workflow contains unresolved placeholders")


def get_node_classes(workflow: dict[str, Any]) -> list[str]:
    return sorted({str(node["class_type"]) for node in workflow.values() if isinstance(node, dict) and "class_type" in node})


def get_checkpoint_name(workflow: dict[str, Any]) -> str:
    for node in workflow.values():
        if isinstance(node, dict) and node.get("class_type") == "CheckpointLoaderSimple":
            inputs = node.get("inputs", {})
            checkpoint = inputs.get("ckpt_name") if isinstance(inputs, dict) else None
            if isinstance(checkpoint, str):
                return checkpoint
    return ""


def has_save_image_node(workflow: dict[str, Any]) -> bool:
    return any(isinstance(node, dict) and node.get("class_type") == "SaveImage" for node in workflow.values())


def has_unresolved_placeholders(value: Any) -> bool:
    if isinstance(value, str):
        return "{{" in value or "}}" in value or value.startswith("__") and value.endswith("__")
    if isinstance(value, list):
        return any(has_unresolved_placeholders(item) for item in value)
    if isinstance(value, dict):
        return any(has_unresolved_placeholders(item) for item in value.values())
    return False
