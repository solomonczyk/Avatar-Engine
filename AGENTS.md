<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes - APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

# Avatar Engine Agent Rules

Avatar Engine is a standalone repository at `F:\Dev\Projects\Avatar Engine`.

Do not treat this folder as part of Gabric. Do not modify, commit, push, clean, reset, restore, or change remotes in the parent repository.

Use the target repository only:

```text
git@github.com:solomonczyk/Avatar-Engine.git
```

Before implementation work, read the documentation in `docs/`, especially:

- `docs/01_PROJECT_SCOPE.md`
- `docs/02_ARCHITECTURE.md`
- `docs/03_COMFY_AGENT_REUSE_PLAN.md`
- `docs/07_GPU_QUEUE_AND_RESOURCE_POLICY.md`
- `docs/13_AGENT_IMPLEMENTATION_BRIEF.md`

This bootstrap layer must stay local, single-user, SQLite-backed, and fake-generation-only for talking-head/lip-sync work. The talking-head job surface may validate parameterized reference images and audio, inspect local runtime candidates, and exercise an explicit fake subprocess adapter in tests, but it must not run real talking-head model inference without a later operator-approved scope change. Do not add Redis, Celery, PostgreSQL, Kubernetes, Docker orchestration, authentication, accounts, roles, public APIs, cloud deployment, distributed workers, multi-agent runtimes, heavy ML dependencies, automatic retry, or unauthorized real generation.
