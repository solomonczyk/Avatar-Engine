import json

import pytest

from avatar_engine.integrations.comfyui.workflow_loader import load_workflow


def test_load_workflow_json_object(tmp_path) -> None:
    path = tmp_path / "workflow.json"
    path.write_text(json.dumps({"1": {"class_type": "Test"}}), encoding="utf-8")
    assert load_workflow(path)["1"]["class_type"] == "Test"


def test_load_workflow_rejects_non_object(tmp_path) -> None:
    path = tmp_path / "workflow.json"
    path.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError):
        load_workflow(path)
