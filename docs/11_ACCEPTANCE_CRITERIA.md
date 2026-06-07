# 11. Acceptance Criteria

## Project bootstrap accepted

- target folder created;
- target repo cloned;
- README and docs present;
- package imports;
- tests run;
- origin points to Avatar-Engine;
- git clean.

## Queue accepted

- job survives application restart;
- jobs execute FIFO;
- second worker cannot acquire GPU lock;
- failed stage stops job;
- no automatic retry.

## ComfyUI accepted

- health check succeeds;
- workflow submitted once;
- outputs collected;
- workflow snapshot saved;
- generation count matches requested count.

## Full avatar accepted technically

- valid input portrait;
- valid audio;
- animation/lip-sync completed;
- final MP4 exists;
- video and audio streams present;
- manifest complete;
- state is `operator_visual_review_required`.

## Full avatar accepted visually

Operator confirms:

- intended identity;
- face visible;
- mouth acceptable;
- no severe eye/teeth artifacts;
- no broken background;
- no obvious frozen output;
- audio understandable;
- lip-sync acceptable for the intended use.

Only then:

```json
{
  "operator_visual_review": "accepted",
  "production_accepted": true
}
```

For this private project `production_accepted` means only “accepted by the operator for personal use”, not commercial production readiness.
