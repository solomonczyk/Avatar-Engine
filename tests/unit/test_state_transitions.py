import pytest

from avatar_engine.jobs.state import JobState, StageState, ensure_job_transition, ensure_stage_transition


def test_valid_job_transition() -> None:
    ensure_job_transition(JobState.QUEUED.value, JobState.RUNNING)


def test_invalid_job_transition_rejected() -> None:
    with pytest.raises(ValueError):
        ensure_job_transition(JobState.QUEUED.value, JobState.ACCEPTED)


def test_valid_stage_transition() -> None:
    ensure_stage_transition(StageState.PENDING.value, StageState.RUNNING)
