# 02. Architecture

## Architectural principle

Минимальная локальная архитектура без enterprise-усложнения.

```text
CLI
 ↓
Job Service
 ↓
SQLite Queue
 ↓
Single Worker
 ↓
Pipeline Stage
 ├─ ComfyUI
 ├─ TTS
 ├─ Talking Avatar / Lip-sync
 └─ FFmpeg
 ↓
Artifacts + Manifest
 ↓
Manual Visual Review
```

## Components

### CLI

Команды:

```text
avatar-engine init
avatar-engine create-job
avatar-engine list-jobs
avatar-engine run-worker
avatar-engine show-job <id>
avatar-engine review <id> --accept
avatar-engine review <id> --reject
```

### Job Service

Отвечает за:

- создание job;
- проверку входных путей;
- запись state;
- формирование stage list;
- чтение статусов;
- отмену ожидающего job.

### SQLite Queue

Одна локальная база:

```text
data/avatar_engine.db
```

Таблицы:

- `jobs`;
- `job_stages`;
- `artifacts`;
- `events`.

### Single Worker

- только один процесс;
- берёт первый `queued` job;
- исполняет стадии последовательно;
- перед GPU-стадией проверяет отсутствие активной GPU-задачи;
- фиксирует stdout, stderr, duration и exit code;
- при ошибке останавливает job;
- не выполняет автоматический retry.

### Pipeline

Базовый MVP pipeline:

```text
validate_inputs
→ prepare_portrait
→ prepare_audio
→ animate_avatar
→ postprocess_video
→ build_manifest
→ operator_visual_review_required
```

Опциональная стадия `generate_portrait` включается только когда действительно нужна генерация изображения.

### Manual Visual Review

Технический успех не означает визуальное принятие.

Финальные состояния:

- `accepted`;
- `rejected`;
- `failed`;
- `cancelled`.

## Why no Redis/Celery

Для одного пользователя и одного компьютера SQLite и один worker проще, прозрачнее и достаточны. Celery, Redis и distributed orchestration не дают практической пользы на MVP и увеличивают количество точек отказа.
