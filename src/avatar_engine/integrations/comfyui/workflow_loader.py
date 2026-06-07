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
    return data
