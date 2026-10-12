# Production state machine

Primary book states:

```
SERIES_PLANNED
BOOK_PLANNED
GENERATING
ART_LOCKED
PREPRESS_PASS
INTERIOR_LOCKED
COVER_LOCKED
METADATA_READY
KDP_DRAFT_READY
HUMAN_APPROVAL
PUBLISHED
```

Scene QA:

```
PLANNED → GENERATED → PASS → ART_LOCKED
                    ↘ FIX_LOCAL
                    ↘ REGENERATE
```

Rules:

- A scene normally gets at most 2 generations.
- A third generation requires a recorded concrete structural/material defect.
- ART_LOCKED cannot be overwritten by a normal production job.
- Microscopic imperfections, antialiasing and harmless asymmetry do not reopen locked art.
- Final publication is never triggered automatically.
