from __future__ import annotations

from copy import deepcopy
from typing import Any


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
