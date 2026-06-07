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

`queued`, `running`, `failed`, `operator_visual_review_required`, `accepted`, `rejected`, `cancelled`.

## Stage states

`pending`, `running`, `completed`, `failed`, `skipped`.

## Manifest minimum

The manifest stores job timestamps, input files, stages, models, workflows, output files, final video path, technical result and operator review status.

## Retention

Nothing is deleted automatically in MVP. Add a manual cleanup command later. Temporary files may be removed only after final artifacts are safely copied.
