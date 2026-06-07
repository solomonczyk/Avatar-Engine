from __future__ import annotations

import json

from avatar_engine.jobs.repository import utc_now
from avatar_engine.pipeline.context import PipelineContext
from avatar_engine.pipeline.stages.base import StageResult, sha256_file
from avatar_engine.models import Artifact


class BuildManifestStage:
    name = "build_manifest"
    uses_gpu = False

    def run(self, context: PipelineContext) -> StageResult:
        job = context.metadata["job"]
        stage_results = context.metadata.get("stage_results", [])
        finished_at = utc_now()
        manifest = {
            "job_id": context.job_id,
            "mode": job.input_json.get("mode", "fake"),
            "created_at": job.created_at,
            "started_at": context.metadata.get("started_at"),
            "finished_at": finished_at,
            "input_files": [value for value in [job.input_json.get("portrait"), job.input_json.get("audio")] if value],
            "stages": stage_results + [{"name": self.name, "status": "completed"}],
            "artifacts": [
                {
                    "stage_name": artifact.stage_name,
                    "artifact_type": artifact.artifact_type,
                    "path": str(artifact.path),
                    "sha256": artifact.sha256,
                    "size_bytes": artifact.size_bytes,
                }
                for artifact in context.artifacts
            ],
            "gpu_stages_executed": 0,
            "comfyui_submit_executed": False,
            "real_generation_executed": False,
            "automatic_retry_executed": False,
            "technical_result": "passed",
            "operator_visual_review": "pending",
            "production_accepted": False,
        }
        path = context.job_dir / "manifest.json"
        path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
        artifact = Artifact(
            artifact_type="manifest",
            path=path,
            sha256=sha256_file(path),
            size_bytes=path.stat().st_size,
            stage_name=self.name,
        )
        return StageResult(artifacts=[artifact], metadata={"manifest_path": str(path)}, stdout="manifest built")
