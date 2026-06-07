from __future__ import annotations

from avatar_engine.pipeline.context import PipelineContext
from avatar_engine.pipeline.stages.base import StageResult, text_artifact


class PreparePortraitStage:
    name = "prepare_portrait"
    uses_gpu = False

    def run(self, context: PipelineContext) -> StageResult:
        artifact = text_artifact(
            context,
            self.name,
            "portrait_placeholder",
            "portrait_placeholder.txt",
            "Fake portrait prepared. No image generation executed.\n",
        )
        return StageResult(artifacts=[artifact], stdout="portrait placeholder prepared")
