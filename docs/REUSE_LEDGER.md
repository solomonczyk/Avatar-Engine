# Reuse Ledger

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
