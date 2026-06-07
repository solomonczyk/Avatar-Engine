# 11. Acceptance Criteria

## Bootstrap accepted

- target folder exists;
- target repository is cloned;
- README and docs are present;
- package imports;
- tests pass;
- `origin` points to Avatar-Engine;
- Git is clean.

## Queue accepted

- jobs survive restart;
- FIFO order works;
- a second worker cannot acquire the GPU lock;
- a failed stage stops the job;
- no automatic retry occurs.

## ComfyUI accepted

- health check succeeds;
- a workflow is submitted once;
- outputs are collected;
- a workflow snapshot is saved;
- generation count matches the request.

## Technical avatar accepted

- portrait and audio inputs are valid;
- animation or lip-sync completes;
- final MP4 exists;
- video and audio streams are present;
- manifest is complete;
- state is `operator_visual_review_required`.

## Visual avatar accepted

The operator confirms intended identity, visible face, understandable audio, acceptable lip-sync and no severe eye, mouth, teeth, background or frozen-frame defects.

Only after that may the result become `accepted`. In this project, accepted means approved for private personal use, not commercial readiness.
