# 13. Agent Implementation Brief

## Task ID

`AVATAR-ENGINE-BOOTSTRAP-AND-DEVELOPMENT-FOUNDATION-001`

## Goal

Create the local project at:

```text
F:\Dev\Projects\Avatar Engine
```

Use the target Git repository:

```text
git@github.com:solomonczyk/Avatar-Engine.git
```

Selectively reuse necessary code and tests from:

```text
https://github.com/solomonczyk/comfy-agent-mvp
```

Build the complete development foundation for a single-user, non-commercial, local Avatar Engine.

## Allowed scope

- clone/init target project;
- inspect source repo;
- copy/adapt only necessary modules;
- create package structure;
- create SQLite queue foundation;
- create single-worker foundation;
- create ComfyUI adapter foundation;
- create config and CLI skeleton;
- create tests;
- create docs and reuse ledger;
- commit and push.

## Forbidden actions

- do not modify `comfy-agent-mvp`;
- do not push to `comfy-agent-mvp`;
- do not copy its full history or data folders;
- do not copy generated assets;
- do not copy secrets;
- do not download model weights;
- do not run real generation;
- do not run ComfyUI workflow;
- do not add Redis/Celery/PostgreSQL/Kubernetes;
- do not add auth, accounts or public API;
- do not build multi-agent runtime;
- do not implement automatic retry;
- do not mark visual or production acceptance.

## Required implementation

1. Clone target repository into exact target folder.
2. Verify `origin`.
3. Create project layout from `04_PROJECT_STRUCTURE.md`.
4. Add `pyproject.toml`.
5. Implement configuration loading.
6. Implement SQLite schema and repository.
7. Implement job/stage state model.
8. Implement FIFO queue service.
9. Implement single-worker lock.
10. Add placeholder pipeline stages with deterministic no-op test mode.
11. Add ComfyUI interface and fake implementation for tests.
12. Add CLI commands:
   - `doctor`;
   - `init-db`;
   - `create-job`;
   - `list-jobs`;
   - `show-job`;
   - `run-worker`.
13. Add `docs/REUSE_LEDGER.md`.
14. Adapt only source modules that are clearly useful and document every one.
15. Add unit and integration tests.
16. Update README with real commands.

## Control points

- target repo only;
- local single-user design;
- SQLite;
- concurrency=1;
- no real generation;
- no retry;
- generated artifacts ignored;
- source reuse traceable.

## Required artifacts

- source tree;
- docs;
- `.env.example`;
- `.gitignore`;
- `pyproject.toml`;
- SQLite schema;
- tests;
- `docs/REUSE_LEDGER.md`;
- `proof_avatar_engine_bootstrap_001.json`.

## Tests

Must prove:

- package imports;
- DB initializes;
- job is persisted;
- FIFO order;
- second worker lock is rejected;
- failed stage stops remaining stages;
- no automatic retry;
- fake pipeline completes;
- no source/project path confusion.

## Verification

```powershell
python -m compileall src
pytest -q
avatar-engine doctor
avatar-engine init-db
avatar-engine create-job --dry-run
avatar-engine list-jobs
git diff --check
git status --short
```

## Proof JSON

```json
{
  "task_id": "AVATAR-ENGINE-BOOTSTRAP-AND-DEVELOPMENT-FOUNDATION-001",
  "target_path": "F:\\Dev\\Projects\\Avatar Engine",
  "target_repo": "git@github.com:solomonczyk/Avatar-Engine.git",
  "source_repo_modified": false,
  "single_user_local_only": true,
  "commercial_solution": false,
  "sqlite_used": true,
  "redis_used": false,
  "celery_used": false,
  "postgresql_used": false,
  "gpu_concurrency": 1,
  "real_generation_executed": false,
  "automatic_retry_enabled": false,
  "tests_passed": true,
  "commit_sha": "",
  "pushed": true,
  "git_clean": true
}
```

## Completion

The task is complete only when:

- implementation and tests pass;
- documentation matches actual code;
- proof JSON exists;
- commit is pushed to `origin/main`;
- working tree is clean.
