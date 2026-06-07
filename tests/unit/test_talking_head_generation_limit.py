import pytest

from avatar_engine.integrations.talking_head.attempts import TalkingHeadAttemptCounters, TalkingHeadAttemptLimitError


def test_talking_head_second_generation_is_blocked() -> None:
    counters = TalkingHeadAttemptCounters()
    counters.mark_started()

    with pytest.raises(TalkingHeadAttemptLimitError):
        counters.before_generate()

    assert counters.to_dict()["talking_head_attempts"] == 1
    assert counters.to_dict()["automatic_retry_executed"] is False
