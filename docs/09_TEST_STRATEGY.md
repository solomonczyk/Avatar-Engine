# 09. Test Strategy

## Unit tests

- state transitions;
- SQLite repository;
- FIFO queue;
- only one running job;
- stale lock handling;
- path validation;
- manifest building;
- workflow patching;
- config parsing.

## Integration tests

- fake ComfyUI server;
- workflow submission parsing;
- output collection;
- subprocess success/failure;
- FFmpeg availability;
- audio probing;
- job restart after process restart.

## Real local tests

Marked separately:

```text
@pytest.mark.local_comfyui
@pytest.mark.gpu
@pytest.mark.e2e
```

They are not required in normal CI.

## E2E acceptance test

Input:

- one portrait;
- one 5–10 second audio;
- one approved workflow.

Expected:

- one queued job;
- one worker;
- one final MP4;
- manifest;
- no overlapping GPU stage;
- state `operator_visual_review_required`;
- operator decision recorded.

## Visual testing

Automated checks can detect:

- file exists;
- duration;
- resolution;
- non-zero frames;
- audio stream;
- frozen/duplicate frame ratio.

They cannot replace the operator’s visual decision.

## Test command

```powershell
pytest -q
```

Optional local:

```powershell
pytest -q -m "local_comfyui or gpu or e2e"
```
