# Automated book design

The current Cozy Little Worlds interior template is deterministic:

- 8.5 x 8.5 inch trim
- 40 illustrations
- illustrations on odd pages
- explicit blank reverse pages
- 80 physical pages
- centered 7.5 x 7.5 inch art area
- no bleed

Cover geometry is calculated from trim size, page count, bleed and an externally supplied spine width. The spine value is not guessed: production must obtain or validate it against the current KDP cover specification/template before final assembly.

PDF preflight checks page count, trim size and page-size consistency. More structural checks will be added before a file can advance to INTERIOR_LOCKED or COVER_LOCKED.
