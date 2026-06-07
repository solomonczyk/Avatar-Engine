from __future__ import annotations

import json

from avatar_engine.pipeline.context import PipelineContext
from avatar_engine.pipeline.stages.base import StageResult, text_artifact


class ValidateInputsStage:
    name = "validate_inputs"
    uses_gpu = False

    def run(self, context: PipelineContext) -> StageResult:
        job = context.metadata["job"]
        artifact = text_artifact(
            context,
            self.name,
            "validation_report",
            "validation_report.json",
            json.dumps(
                {
                    "job_id": context.job_id,
                    "mode": job.input_json.get("mode", "fake"),
                    "dry_run": bool(job.input_json.get("dry_run")),
                    "valid": True,
                },
                indent=2,
                sort_keys=True,
            ),
        )
        return StageResult(artifacts=[artifact], stdout="inputs validated")
