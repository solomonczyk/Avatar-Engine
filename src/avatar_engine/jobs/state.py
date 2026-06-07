from __future__ import annotations

from enum import StrEnum


class JobState(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    FAILED = "failed"
    OPERATOR_VISUAL_REVIEW_REQUIRED = "operator_visual_review_required"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class StageState(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


JOB_TRANSITIONS: dict[JobState, set[JobState]] = {
    JobState.QUEUED: {JobState.RUNNING, JobState.CANCELLED},
    JobState.RUNNING: {JobState.FAILED, JobState.OPERATOR_VISUAL_REVIEW_REQUIRED, JobState.CANCELLED},
    JobState.FAILED: set(),
    JobState.OPERATOR_VISUAL_REVIEW_REQUIRED: {JobState.ACCEPTED, JobState.REJECTED},
    JobState.ACCEPTED: set(),
    JobState.REJECTED: set(),
    JobState.CANCELLED: set(),
}

STAGE_TRANSITIONS: dict[StageState, set[StageState]] = {
    StageState.PENDING: {StageState.RUNNING, StageState.SKIPPED},
    StageState.RUNNING: {StageState.COMPLETED, StageState.FAILED},
    StageState.COMPLETED: set(),
    StageState.FAILED: set(),
    StageState.SKIPPED: set(),
}


def ensure_job_transition(current: str, target: JobState) -> None:
    state = JobState(current)
    if target not in JOB_TRANSITIONS[state]:
        raise ValueError(f"Invalid job transition: {state.value} -> {target.value}")


def ensure_stage_transition(current: str, target: StageState) -> None:
    state = StageState(current)
    if target not in STAGE_TRANSITIONS[state]:
        raise ValueError(f"Invalid stage transition: {state.value} -> {target.value}")
