# 13. Agent Implementation Brief

Task: `AVATAR-ENGINE-BOOTSTRAP-AND-DEVELOPMENT-FOUNDATION-001`

Create the project in `F:\Dev\Projects\Avatar Engine` and use `git@github.com:solomonczyk/Avatar-Engine.git` as the only development repository.

Use `solomonczyk/comfy-agent-mvp` only as a read-only reference. Adapt only the required ComfyUI client, workflow patching, artifact manifest and relevant test patterns. Record every adapted file in the reuse ledger.

Build a Python 3.11 package with configuration loading, SQLite job persistence, FIFO execution, one worker lock, deterministic test pipeline stages, a ComfyUI interface, CLI commands and tests.

The foundation remains local, single-user and non-commercial. It does not include real generation, model downloads, automatic retry, distributed services, authentication, public API or multi-agent orchestration.

Completion requires passing tests, updated documentation, a proof JSON file, a pushed commit and clean Git.
