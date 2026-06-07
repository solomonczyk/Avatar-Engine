from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class WorkflowPatchReport:
    patched_fields: list[str]
    missing_targets: list[str]
    workflow_changed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "patched_fields": self.patched_fields,
            "missing_targets": self.missing_targets,
            "workflow_changed": self.workflow_changed,
        }


def patch_workflow(workflow: dict[str, Any], replacements: dict[str, Any]) -> dict[str, Any]:
    patched = deepcopy(workflow)
    for dotted_path, value in replacements.items():
        parts = dotted_path.split(".")
        cursor: Any = patched
        for part in parts[:-1]:
            if isinstance(cursor, list):
                cursor = cursor[int(part)]
            else:
                cursor = cursor.setdefault(part, {})
        last = parts[-1]
        if isinstance(cursor, list):
            cursor[int(last)] = value
        else:
            cursor[last] = value
    return patched


def patch_controlled_inputs(
    workflow: dict[str, Any],
    *,
    checkpoint: str,
    positive_prompt: str,
    negative_prompt: str,
    seed: int,
    width: int,
    height: int,
    steps: int,
    cfg: float,
    output_prefix: str,
    sampler: str = "euler",
    scheduler: str = "normal",
) -> tuple[dict[str, Any], WorkflowPatchReport]:
    patched = deepcopy(workflow)
    patched_fields: list[str] = []
    missing_targets: list[str] = []

    checkpoint_node = _first_node_id(patched, "CheckpointLoaderSimple")
    sampler_node = _first_node_id(patched, "KSampler")
    latent_node = _first_node_id(patched, "EmptyLatentImage")
    save_node = _first_node_id(patched, "SaveImage")
    text_nodes = _node_ids(patched, "CLIPTextEncode")

    _patch_input(patched, checkpoint_node, "ckpt_name", checkpoint, patched_fields, missing_targets)
    _patch_input(patched, sampler_node, "seed", seed, patched_fields, missing_targets)
    _patch_input(patched, sampler_node, "steps", steps, patched_fields, missing_targets)
    _patch_input(patched, sampler_node, "cfg", cfg, patched_fields, missing_targets)
    _patch_input(patched, sampler_node, "sampler_name", sampler, patched_fields, missing_targets)
    _patch_input(patched, sampler_node, "scheduler", scheduler, patched_fields, missing_targets)
    _patch_input(patched, latent_node, "width", width, patched_fields, missing_targets)
    _patch_input(patched, latent_node, "height", height, patched_fields, missing_targets)
    _patch_input(patched, latent_node, "batch_size", 1, patched_fields, missing_targets)
    _patch_input(patched, text_nodes[0] if len(text_nodes) >= 1 else None, "text", positive_prompt, patched_fields, missing_targets)
    _patch_input(patched, text_nodes[1] if len(text_nodes) >= 2 else None, "text", negative_prompt, patched_fields, missing_targets)
    _patch_input(patched, save_node, "filename_prefix", output_prefix, patched_fields, missing_targets)

    return patched, WorkflowPatchReport(
        patched_fields=patched_fields,
        missing_targets=missing_targets,
        workflow_changed=patched != workflow,
    )


def _node_ids(workflow: dict[str, Any], class_type: str) -> list[str]:
    return [node_id for node_id, node in workflow.items() if isinstance(node, dict) and node.get("class_type") == class_type]


def _first_node_id(workflow: dict[str, Any], class_type: str) -> str | None:
    node_ids = _node_ids(workflow, class_type)
    return node_ids[0] if node_ids else None


def _patch_input(
    workflow: dict[str, Any],
    node_id: str | None,
    input_name: str,
    value: Any,
    patched_fields: list[str],
    missing_targets: list[str],
) -> None:
    if node_id is None:
        missing_targets.append(f"*.inputs.{input_name}")
        return
    node = workflow.get(node_id)
    if not isinstance(node, dict) or not isinstance(node.get("inputs"), dict) or input_name not in node["inputs"]:
        missing_targets.append(f"{node_id}.inputs.{input_name}")
        return
    node["inputs"][input_name] = value
    patched_fields.append(f"{node_id}.inputs.{input_name}")
