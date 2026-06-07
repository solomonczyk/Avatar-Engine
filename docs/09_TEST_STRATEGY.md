# 09. Test Strategy

## Real ComfyUI image tests

Normal `pytest -q` uses fake clients and does not require local ComfyUI. Coverage now includes:

- successful submit parsing;
- malformed prompt ID rejection;
- wait timeout without retry;
- missing workflow patch target reports;
- second submit blocking;
- invalid/blank image rejection;
- valid image technical acceptance;
- `comfyui_image` job stopping at `operator_visual_review_required`.

Real local tests should use:

```text
@pytest.mark.local_comfyui
@pytest.mark.gpu
@pytest.mark.real_generation
```

## Talking-head tests

Normal `pytest -q` uses generated local fixtures and an explicit fake subprocess adapter. Coverage includes:

- parameterized reference-image job input;
- proof that the test reference image is not hardcoded;
- reference image validation;
- audio validation and normalization;
- runtime selection blocker artifacts;
- one-attempt generation limit;
- fake subprocess adapter logs/output;
- MP4 technical validation;
- manifest and operator review packet flags;
- worker flow, no-retry failure, and output isolation.

Real talking-head tests must be marked:

```text
@pytest.mark.local_talking_head
@pytest.mark.gpu
@pytest.mark.real_generation
```

They are skipped from the normal suite until runtime assets and an executable adapter are explicitly authorized.

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

The test suite uses a project-local pytest temp folder under `data/runtime/pytest` so Windows temp-folder permissions do not affect repeatability.

Optional local:

```powershell
pytest -q -m "local_comfyui or gpu or e2e"
```
