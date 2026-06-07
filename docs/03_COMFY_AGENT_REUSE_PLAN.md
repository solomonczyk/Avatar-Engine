# 03. Reuse Plan from comfy-agent-mvp

Источник:

```text
https://github.com/solomonczyk/comfy-agent-mvp
```

## Правило переноса

Не копировать весь репозиторий. Переносить только отдельные модули или идеи после проверки зависимостей и лицензий.

Для каждого переноса фиксировать:

- исходный путь;
- целевой путь;
- зачем нужен;
- какие зависимости тащит;
- что изменено;
- какие тесты перенесены;
- commit source SHA;
- лицензионный статус.

## Что стоит переиспользовать

### ComfyUI client/runtime

Полезны:

- отправка workflow;
- ожидание завершения;
- получение output paths;
- обработка ошибок ComfyUI;
- timeout;
- сохранение prompt/workflow snapshot.

### Workflow loading and patching

Полезны:

- чтение workflow JSON;
- подстановка checkpoint;
- подстановка reference image;
- подстановка prompt;
- seed;
- width/height;
- output prefix.

### Artifact and manifest patterns

Полезны:

- manifest выполнения;
- список входных и выходных файлов;
- длительность стадий;
- workflow id;
- seed/model metadata;
- итоговый статус.

### Character reference binding

Можно использовать идеи:

- canonical reference folder;
- SHA256 inventory;
- reference validation;
- запрет случайной подмены входного лица.

Для single-user MVP не нужен сложный registry агентов и многоступенчатые approval-пакеты.

### TTS adapters

Перенести только реально используемый локальный или API adapter.

### Tests and fixtures

Перенести тесты для:

- workflow patching;
- ComfyUI response parsing;
- artifact manifest;
- reference-path validation;
- deterministic state transitions.

## Что не переносить

- исторические RC proof-пакеты;
- episode-specific data;
- старые acceptance reports;
- production state machines;
- multi-agent registry;
- роли Director/QA/Script Supervisor как отдельные runtime-агенты;
- сложные operator authorization chains;
- PostgreSQL;
- cloud deployment;
- distributed task execution;
- legacy workflows;
- Windsurf-specific runtime logic;
- generated images, videos и model weights.

## Copy ledger

Создать файл:

```text
docs/REUSE_LEDGER.md
```

Пример записи:

```markdown
## REUSE-001

- Source repo: solomonczyk/comfy-agent-mvp
- Source commit: <sha>
- Source path: app/.../comfy_client.py
- Target path: src/avatar_engine/integrations/comfyui/client.py
- Reuse type: adapted copy
- Changes: removed project-specific state, simplified settings
- Tests: tests/integrations/test_comfyui_client.py
- License checked: yes/no
```
