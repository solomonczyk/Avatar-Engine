# 08. Data and Artifacts

## Job folder

```text
data/jobs/<job_id>/
├─ job.json
├─ input/
├─ work/
├─ output/
├─ logs/
├─ workflow/
├─ manifest.json
└─ review.json
```

## Job states

```text
queued
running
failed
operator_visual_review_required
accepted
rejected
cancelled
```

## Stage states

```text
pending
running
completed
failed
skipped
```

## Manifest

Minimum:

```json
{
  "job_id": "job-...",
  "created_at": "...",
  "started_at": "...",
  "finished_at": "...",
  "input_files": [],
  "stages": [],
  "models": [],
  "workflows": [],
  "output_files": [],
  "final_video": null,
  "technical_result": "passed",
  "operator_visual_review": "pending"
}
```

## Review

```json
{
  "job_id": "job-...",
  "decision": "accepted",
  "reviewed_at": "...",
  "notes": "..."
}
```

## Retention

Поскольку решение локальное и single-user:

- ничего автоматически не удалять в MVP;
- добавить ручную команду cleanup позже;
- models хранить отдельно;
- temp можно очищать только после успешного копирования финальных artifacts.
