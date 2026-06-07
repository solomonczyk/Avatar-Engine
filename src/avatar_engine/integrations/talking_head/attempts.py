from __future__ import annotations

from dataclasses import dataclass


class TalkingHeadAttemptLimitError(RuntimeError):
    pass


@dataclass
class TalkingHeadAttemptCounters:
    talking_head_attempts: int = 0
    max_talking_head_generations: int = 1
    automatic_retry_enabled: bool = False
    automatic_retry_executed: bool = False
    second_runtime_attempted: bool = False

    def before_generate(self) -> None:
        if self.talking_head_attempts >= self.max_talking_head_generations:
            raise TalkingHeadAttemptLimitError("Only one talking-head generation is allowed")

    def mark_started(self) -> None:
        self.before_generate()
        self.talking_head_attempts += 1

    def mark_second_runtime_attempted(self) -> None:
        self.second_runtime_attempted = True
        raise TalkingHeadAttemptLimitError("Switching runtime after the first attempt is blocked")

    def to_dict(self) -> dict[str, object]:
        return {
            "talking_head_attempts": self.talking_head_attempts,
            "max_talking_head_generations": self.max_talking_head_generations,
            "automatic_retry_enabled": self.automatic_retry_enabled,
            "automatic_retry_executed": self.automatic_retry_executed,
            "second_runtime_attempted": self.second_runtime_attempted,
        }
