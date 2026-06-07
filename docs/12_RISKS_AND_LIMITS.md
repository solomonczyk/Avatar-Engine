# 12. Risks and Limits

## Hardware

GTX 1060 5 GB limits:

- SDXL may require low-VRAM workflow;
- LivePortrait can be unstable depending on build;
- high-resolution video inference may fail;
- AI upscale can consume most VRAM;
- simultaneous models are prohibited.

Mitigation:

- 512/768-class working resolution;
- one GPU process;
- subprocess isolation;
- cloud/API portrait generation only as optional fallback;
- final upscale only after visual acceptance.

## Dependency conflicts

SadTalker, LivePortrait and other repositories may require different Python/Torch versions.

Mitigation:

- separate virtual environments;
- call runtimes through subprocess adapters;
- pin versions;
- do not create one huge `requirements.txt`.

## Visual quality

Technical completion does not guarantee:

- identity preservation;
- natural eyes;
- natural teeth;
- good lip-sync;
- good head movement.

Mitigation:

- approved portrait input;
- short test audio;
- manual review;
- one controlled correction after explicit operator decision.

## Licensing

This is a non-commercial personal solution, but licenses still matter.

Before adding a model:

- record source;
- record license;
- record commercial/non-commercial restriction;
- do not redistribute weights;
- use only faces and voices with permission.

## Scope creep

Main risk is rebuilding the entire `comfy-agent-mvp`.

Mitigation:

- copy only necessary modules;
- no multi-agent system in MVP;
- no cloud;
- no user management;
- no complex security layer;
- no autonomous retries.
