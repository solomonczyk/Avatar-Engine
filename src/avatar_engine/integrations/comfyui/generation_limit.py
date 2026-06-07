from __future__ import annotations

from dataclasses import dataclass


class GenerationLimitError(RuntimeError):
    pass


@dataclass
class GenerationCounters:
    submit_attempts: int = 0
    successful_submits: int = 0
    generation_attempts: int = 0
    max_generations: int = 1

    def before_submit(self) -> None:
        if self.generation_attempts != 0:
            raise GenerationLimitError("ComfyUI generation was already attempted for this job")
        if self.generation_attempts >= self.max_generations:
            raise GenerationLimitError("ComfyUI max generation count reached")

    def mark_submit_attempt(self) -> None:
        self.submit_attempts += 1
        self.generation_attempts += 1

    def mark_successful_submit(self) -> None:
        self.successful_submits += 1

    def to_dict(self) -> dict[str, int]:
        return {
            "submit_attempts": self.submit_attempts,
            "successful_submits": self.successful_submits,
            "generation_attempts": self.generation_attempts,
            "max_generations": self.max_generations,
        }
