# Production worker

The production worker consumes one scene at a time.

1. GENERATE_SCENE
2. REVIEW_SCENE
3. PASS -> ART_LOCKED -> enqueue next scene
4. FIX_LOCAL -> enqueue corrected generation
5. REGENERATE -> record material defect -> enqueue regeneration
6. After 40 locked scenes the book advances to ART_LOCKED.

The repository includes mock providers so the complete orchestration can be tested without spending generation credits. Production providers will use private server-side credentials and private artifact storage.
