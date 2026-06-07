# 08. Data and Artifacts

## Talking-head job folder

```text
data/jobs/<job_id>/
├─ job.json
├─ input/
│  ├─ reference/
│  └─ audio/
├─ preflight/
│  ├─ reference_image_validation.json
│  ├─ audio_validation.json
│  ├─ talking_head_runtime_selection.json
│  └─ talking_head_runtime_preflight.json
├─ work/
│  └─ talking_head/
├─ output/
│  └─ <job_id>_talking_head.mp4
├─ preview/
│  ├─ first_frame.png
│  ├─ middle_frame.png
│  ├─ last_frame.png
│  └─ contact_sheet.png
├─ logs/
│  ├─ runtime_command.json
│  ├─ runtime_stdout.log
│  └─ runtime_stderr.log
├─ video_validation.json
├─ manifest.json
└─ operator_review_packet.json
```

If runtime selection blocks, execution artifacts are absent and `talking_head_attempts` remains `0`.

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
