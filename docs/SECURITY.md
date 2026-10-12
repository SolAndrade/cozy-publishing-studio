# Security boundary

This repository is public and GitHub Pages is a public static frontend.

## Never commit

- AI provider API keys
- Amazon/KDP credentials
- browser cookies or sessions
- private generated book assets
- unpublished commercial metadata if it should remain confidential
- tokens, passwords or personal data

The production backend must use server-side environment secrets and private storage. The browser receives only the minimum data required by the dashboard.

Final KDP publication remains a human action.
