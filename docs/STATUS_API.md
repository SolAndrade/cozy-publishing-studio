# System status

The dashboard may request `GET /api/status` to display backend/provider readiness.

The endpoint must expose only provider names, readiness states, and booleans indicating whether required secrets are configured. Secret values are never returned.

This makes missing production configuration visible without leaking credentials into the public GitHub Pages application.
