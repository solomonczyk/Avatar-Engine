# 03. Reuse Plan from comfy-agent-mvp

Source: https://github.com/solomonczyk/comfy-agent-mvp

## Rule

Do not copy the whole repository. Reuse only modules that are required by Avatar Engine. For every copied or adapted file, record the source commit, source path, target path, reason, changes, dependencies, tests, and license status in `docs/REUSE_LEDGER.md`.

## Reuse candidates

- ComfyUI client: workflow submit, polling, output collection, timeout and error parsing.
- Workflow loader and patcher: prompt, seed, model, reference image, width, height and output prefix.
- Artifact manifest patterns.
- Character reference inventory and SHA256 validation.
- The actually selected TTS adapter.
- Tests for workflow patching, response parsing, manifests, reference paths and state transitions.

## Do not reuse

- historical RC proof packages;
- episode-specific data;
- generated images, video, audio or model weights;
- old acceptance reports;
- production multi-agent registry;
- role agents that are not required by this private application;
- distributed execution;
- PostgreSQL, Redis or Celery;
- cloud deployment;
- Windsurf runtime logic;
- legacy workflows that are not used by Avatar Engine.

## Required adaptation

Remove project-specific state and simplify configuration for one local operator. The source repository remains read-only and all Avatar Engine changes are committed only to `solomonczyk/Avatar-Engine`.
