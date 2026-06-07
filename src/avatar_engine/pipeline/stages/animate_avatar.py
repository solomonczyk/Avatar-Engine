from __future__ import annotations

from avatar_engine.pipeline.context import PipelineContext
from avatar_engine.pipeline.stages.base import StageResult, text_artifact


class AnimateAvatarStage:
    name = "animate_avatar"
    uses_gpu = False

    def run(self, context: PipelineContext) -> StageResult:
        artifact = text_artifact(
            context,
            self.name,
            "animation_placeholder",
            "animation_placeholder.txt",
            "Fake avatar animation completed. No ComfyUI submit, GPU command, or video generation executed.\n",
        )
        return StageResult(
            artifacts=[artifact],
            metadata={
                "gpu_executed": False,
                "comfyui_submit_executed": False,
                "real_generation_executed": False,
            },
            stdout="avatar animation placeholder prepared",
        )
