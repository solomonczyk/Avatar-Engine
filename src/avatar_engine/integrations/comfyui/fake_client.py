from __future__ import annotations

from pathlib import Path

from avatar_engine.models import Artifact, HealthResult, HistoryResult, SubmitResult


class FakeComfyUIClient:
    prompt_id = "fake-prompt-avatar-engine-0001"

    def health(self) -> HealthResult:
        return HealthResult(available=True, status="available", details={"fake": True})

    def submit_workflow(self, workflow: dict) -> SubmitResult:
        return SubmitResult(
            prompt_id=self.prompt_id,
            submitted=False,
            details={"fake": True, "workflow_keys": sorted(workflow.keys())},
        )

    def get_history(self, prompt_id: str) -> HistoryResult:
        return HistoryResult(prompt_id=prompt_id, status="completed", details={"fake": True})

    def collect_outputs(self, prompt_id: str) -> list[Artifact]:
        return [
            Artifact(
                artifact_type="fake_comfyui_output_metadata",
                path=Path(f"fake://{prompt_id}/metadata.json"),
                sha256="",
                size_bytes=0,
                stage_name="fake_comfyui",
            )
        ]
