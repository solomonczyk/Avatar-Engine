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
- subprocess success and failure;
- FFmpeg availability;
- audio probing;
- restart recovery.

## Real local tests

Use separate markers: `local_comfyui`, `gpu`, and `e2e`. They are not required in ordinary CI.

## End-to-end acceptance

One portrait and one short audio input must produce one final MP4, a manifest and the state `operator_visual_review_required`. No GPU stages may overlap.

Automated checks verify file existence, duration, resolution, video/audio streams and basic frozen-frame detection. They never replace manual visual review.
