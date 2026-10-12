# Quality pipeline

Cozy Publishing Studio uses two QA layers.

## Deterministic preflight

Code checks dimensions, decodability, tonal characteristics, scene counts, duplicate manifest entries, lock completeness and generation-policy violations.

## Semantic visual review

A vision provider judges composition, structural plausibility, colorability, style identity, unwanted text and material tonal rendering. It must return only PASS, FIX_LOCAL or REGENERATE.

The system does not reopen ART_LOCKED scenes for microscopic issues. Whole-book audit runs before prepress and artifact assembly.
