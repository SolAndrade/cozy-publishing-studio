# Book profiles

Book geometry is configuration, not a global assumption.

Built-in profiles:

- **Cozy Square 8.5 × 8.5** — current Cozy Little Worlds format.
- **Classic Portrait 8.5 × 11** — portrait format used by earlier coloring books.
- **Custom** — explicit trim, art area, scene count, blank-reverse and bleed settings.

A series may choose a default profile, while an individual book may override it. Production code must read the selected profile before building interiors or covers.

KDP-dependent values such as final cover dimensions, permitted trim/bleed combinations and spine width must be validated against current KDP requirements at production time rather than treated as permanent constants.
