# Completion pipeline

After all scene art is locked, progression is gated and deterministic:

ART_LOCKED -> whole-book audit -> PREPRESS_PASS -> interior build/preflight -> INTERIOR_LOCKED -> cover build/preflight -> COVER_LOCKED -> metadata validation -> METADATA_READY.

A failed gate never advances state.

Cover content is separated from cover geometry. Geometry comes from the selected Book Profile plus a spine width that must be externally validated for the current publishing specification. This allows square, portrait and future custom books to use the same workflow.
