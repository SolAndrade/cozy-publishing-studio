# Secrets and publishing readiness

Secrets are backend-only environment variables. They must never be embedded in GitHub Pages, committed to this public repository, or returned by status endpoints.

The system may expose only whether a required secret is configured.

Publishing readiness distinguishes three states:

- READY: machine prerequisite is satisfied.
- BLOCKED: a technical prerequisite is missing.
- HUMAN: a deliberate human action is required.

The KDP draft connector remains BLOCKED until a currently authorized and reliable integration mechanism is validated. Final publication remains HUMAN even after draft preparation is automated.
