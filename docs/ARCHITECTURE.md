# Architecture v0.1

## Principles

1. Human approval is final.
2. Locked assets are immutable by default.
3. Stop only for material defects, missing required information, or a real human decision.
4. Deterministic code handles objective checks; models handle semantic/visual judgments.
5. No secrets or private publishing data in the GitHub Pages frontend.
6. Every generation, regeneration, QA decision and artifact is auditable.

## Domains

- Series Planner: proposes exactly five differentiated books and scores them against a fixed rubric.
- Book Planner: produces a locked book brief and scene manifest.
- Art Director: converts scenes into bounded generation instructions.
- Image Pipeline: generation, retries and asset versioning.
- QA: PASS / FIX_LOCAL / REGENERATE with strict retry limits.
- Prepress: deterministic image/PDF checks and assembly.
- Cover: template-driven cover package.
- Metadata: title, subtitle, description, keywords, categories and AI-content declarations.
- KDP: draft preparation/integration. No automatic final publish action.
- Approval: presents the final package to the owner.

## Deployment

GitHub Pages hosts only the static UI. A private backend will later own orchestration, credentials, generation jobs, storage and KDP-related operations.
