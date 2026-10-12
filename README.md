# Cozy Publishing Studio

Automation-first production studio for creating coherent coloring-book series and preparing publication-ready book packages.

## Product goal

Create series of 5 books with a quality-gated workflow and one meaningful human approval at the end.

```
SERIES_PLANNED → BOOK_PLANNED → GENERATING → ART_LOCKED → PREPRESS_PASS
→ INTERIOR_LOCKED → COVER_LOCKED → METADATA_READY → KDP_DRAFT_READY → HUMAN_APPROVAL
```

Locked assets are immutable unless a material defect is explicitly recorded.

## v0.1

The first release is a friendly Spanish dashboard hosted as a static frontend. It models series, five-book plans, production states and the approval queue. The production engine and secrets will live outside GitHub Pages.

## Run locally

Open `index.html`, or serve the repository with any static web server.

## Security

Never commit API keys, Amazon credentials, session cookies, generated private assets, or customer/account data. GitHub Pages is treated as an untrusted static frontend.

## Next milestones

1. Persistent project schema and production state machine.
2. Series/book planning engine with fixed rubrics.
3. Image generation + FAST QA pipeline.
4. Prepress/interior/cover builders and deterministic validation.
5. Metadata/KDP package generation.
6. Authorized KDP draft integration, only after current platform rules are verified.
