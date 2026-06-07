# 05. Development Plan

## Milestone 2 status

ComfyUI integration now includes local health checks, typed submit/history/output collection, workflow patch reporting, a one-image `comfyui_image` job mode, technical image validation, manifest generation, and an operator review packet.

Stop point: `operator_visual_review_required`. The next layer starts only after manual operator review of the actual image.

## Milestone 0 — Bootstrap and selective import

Result:

- repository cloned into target folder;
- Python package created;
- documentation committed;
- source repo added as temporary read-only reference or cloned beside project;
- reuse ledger created;
- tests run;
- Git clean.

No generation.

## Milestone 1 — Local job queue and worker

Result:

- SQLite schema;
- create/list/show job commands;
- one worker;
- sequential stage execution;
- restart-safe queue;
- stage logs;
- failed jobs stop;
- no automatic retry.

No ComfyUI required for unit tests.

## Milestone 2 — ComfyUI integration

Result:

- local health check;
- submit workflow;
- poll history;
- collect outputs;
- workflow patching;
- one real image output;
- manifest.

## Milestone 3 — Audio

Result:

- accept existing WAV/MP3;
- optional TTS adapter;
- normalize audio with FFmpeg;
- save duration and sample rate.

## Milestone 4 — Talking avatar

Choose one runtime that works on the actual hardware.

Priority:

1. existing proven ComfyUI nodes/workflow;
2. SadTalker;
3. MuseTalk/Wav2Lip;
4. LivePortrait only if VRAM and dependencies permit.

Result:

- portrait + audio → video;
- no second simultaneous GPU model;
- model/process is released before next GPU stage.

## Milestone 5 — Postprocessing and visual review

Result:

- FFmpeg encode;
- final MP4;
- preview frame/contact sheet;
- operator review command;
- accepted/rejected result;
- no automatic acceptance.

## Milestone 6 — Convenience UI

Only after E2E works.

Possible:

- minimal FastAPI localhost;
- minimal Gradio;
- simple web page for create/status/review.

Do not build UI before the CLI E2E is stable.

## Completion rule for each milestone

- implementation;
- tests;
- artifacts;
- proof JSON;
- updated docs;
- commit;
- push;
- clean Git.
