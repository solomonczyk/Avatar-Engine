# 12. Risks and Limits

## Hardware

GTX 1060 5 GB may limit high-resolution image and video models. Use one GPU process, moderate working resolution, subprocess isolation and final upscale only after visual acceptance.

## Dependency conflicts

Talking-avatar and lip-sync repositories may require different Python and Torch versions. Keep separate virtual environments and call them through subprocess adapters. Do not force every model into one dependency set.

## Visual quality

Technical completion does not guarantee identity preservation, natural eyes, teeth, mouth motion or good lip-sync. Use an approved portrait, short test audio and manual review.

## Licensing

This project is non-commercial, but licenses still apply. Record every model source and license, do not redistribute weights and use only faces and voices with permission.

## Scope creep

Do not rebuild the entire source project. Copy only required modules. Do not add multi-user features, cloud deployment, distributed execution, autonomous retry or a large agent hierarchy.
