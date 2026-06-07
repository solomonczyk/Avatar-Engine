# Reuse Ledger

### REUSE-007

- Source repository: none
- Source commit: not applicable
- Source path: clean-room talking-head runtime selection and validation design
- Target path: src/avatar_engine/integrations/talking_head, src/avatar_engine/pipeline/stages/talking_head.py
- Reuse type: original
- Reason: Add parameterized reference-image talking-head job control without hardcoding a test identity or running unauthorized model inference.
- Changes: Implemented fresh reference/audio/video validators, runtime selection artifacts, fake subprocess adapter, one-attempt counters, manifest, and operator review packet.
- Dependencies: Python standard library, Pillow, local FFmpeg/FFprobe
- Tests: tests/unit/test_reference_image_job_input.py, tests/unit/test_reference_image_not_hardcoded.py, tests/unit/test_reference_image_validation.py, tests/unit/test_audio_validation.py, tests/unit/test_talking_head_runtime_selection.py, tests/unit/test_talking_head_generation_limit.py, tests/unit/test_talking_head_subprocess_adapter.py, tests/unit/test_video_validation.py, tests/unit/test_talking_head_manifest.py, tests/integration/test_talking_head_fake_runtime.py, tests/integration/test_talking_head_worker_flow.py, tests/integration/test_talking_head_failure_no_retry.py, tests/integration/test_talking_head_output_isolation.py
- License reviewed: no source code copied

### REUSE-005

- Source repository: https://github.com/solomonczyk/comfy-agent-mvp
- Source commit: local reference at F:\ComfyUI\comfy-agent-mvp, exact commit not required because source code was not copied
- Source path: data/workflows/sdxl_txt2img_template.json
- Target path: workflows/simple_portrait.json
- Reuse type: concept_only
- Reason: Use the standard simple txt2img ComfyUI shape for one controlled image generation.
- Changes: Wrote a fresh minimal workflow for Avatar Engine with 512x512, batch size 1, 15 steps, neutral fictional prompt, and `SaveImage` prefix under `avatar_engine/<job_id>`.
- Dependencies: existing local ComfyUI nodes and installed checkpoint only
- Tests: tests/unit/test_workflow_loader.py, tests/unit/test_workflow_patch_report.py, live preflight artifact under data/jobs/<job_id>/preflight/comfyui_preflight.json
- License reviewed: source code not copied

### REUSE-006

- Source repository: https://github.com/solomonczyk/comfy-agent-mvp
- Source commit: local reference at F:\ComfyUI\comfy-agent-mvp, exact commit not required because source code was not copied
- Source path: ComfyUI submit/history/output collection concepts
- Target path: src/avatar_engine/integrations/comfyui/client.py, src/avatar_engine/pipeline/stages/comfyui_image.py
- Reuse type: concept_only
- Reason: Implement the first real ComfyUI HTTP path while preserving local-only, one-submit constraints.
- Changes: Implemented fresh typed response handling, timeout, history polling, one-image download, manifest, and operator review packet.
- Dependencies: httpx, Pillow
- Tests: tests/unit/test_comfyui_client_responses.py, tests/unit/test_comfyui_wait_timeout.py, tests/unit/test_generation_limit.py, tests/unit/test_image_validation.py, tests/unit/test_real_job_state_transitions.py
- License reviewed: source code not copied

This file records every copied or adapted component from `solomonczyk/comfy-agent-mvp`.

No source file was copied into Avatar Engine in this bootstrap. The reference repository clone timed out before checkout, so implementation was written as small clean-room modules using only documented concepts. Source HEAD was checked with `git ls-remote`.

### REUSE-001

- Source repository: https://github.com/solomonczyk/comfy-agent-mvp
- Source commit: 8f82d90d310601b9b14954e89f7bd578b7838df2
- Source path: ComfyUI client patterns
- Target path: src/avatar_engine/integrations/comfyui
- Reuse type: concept_only
- Reason: Keep a typed ComfyUI boundary while preventing real generation in bootstrap.
- Changes: Implemented fresh `Protocol`, fake client, and health-check-only HTTP client.
- Dependencies: httpx
- Tests: tests/integration/test_fake_comfyui_client.py
- License reviewed: source code not copied

### REUSE-002

- Source repository: https://github.com/solomonczyk/comfy-agent-mvp
- Source commit: 8f82d90d310601b9b14954e89f7bd578b7838df2
- Source path: workflow loading and patching concepts
- Target path: src/avatar_engine/integrations/comfyui/workflow_loader.py, src/avatar_engine/integrations/comfyui/workflow_patcher.py
- Reuse type: concept_only
- Reason: Provide safe JSON workflow utilities for later ComfyUI layers.
- Changes: Implemented small JSON object loader and dotted-path patcher from scratch.
- Dependencies: Python standard library
- Tests: tests/unit/test_workflow_loader.py, tests/unit/test_workflow_patcher.py
- License reviewed: source code not copied

### REUSE-003

- Source repository: https://github.com/solomonczyk/comfy-agent-mvp
- Source commit: 8f82d90d310601b9b14954e89f7bd578b7838df2
- Source path: artifact manifest and hashing concepts
- Target path: src/avatar_engine/pipeline/stages/build_manifest.py, src/avatar_engine/pipeline/stages/base.py
- Reuse type: concept_only
- Reason: Record deterministic fake job artifacts and proof flags.
- Changes: Implemented fresh manifest builder with explicit no-generation flags.
- Dependencies: Python standard library
- Tests: tests/unit/test_manifest.py
- License reviewed: source code not copied

### REUSE-004

- Source repository: https://github.com/solomonczyk/comfy-agent-mvp
- Source commit: 8f82d90d310601b9b14954e89f7bd578b7838df2
- Source path: process/subprocess execution concept
- Target path: src/avatar_engine/resources/process_runner.py
- Reuse type: concept_only
- Reason: Reserve a small subprocess boundary for future FFmpeg/runtime calls.
- Changes: Implemented fresh `run_process` helper with captured stdout/stderr.
- Dependencies: Python standard library
- Tests: covered indirectly by compile/import checks
- License reviewed: source code not copied

## Template

### REUSE-XXX

- Source repository:
- Source commit:
- Source path:
- Target path:
- Reuse type:
- Reason:
- Changes:
- Dependencies:
- Tests:
- License reviewed:
