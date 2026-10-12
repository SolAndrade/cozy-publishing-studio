# Deployment

## Frontend

The static dashboard is deployed by GitHub Actions to GitHub Pages.

## Private backend

GitHub Pages cannot execute Python or protect provider secrets. Deploy the Python service separately. A Render blueprint is included in `render.yaml`.

Required production configuration is server-side only. Never add provider keys to the public frontend.

After deployment, set the frontend API base URL in `config.js` to the HTTPS backend origin.

## Health check

`GET /health` returns a small JSON status response.

## Current boundary

The API skeleton can create a validated five-book series. AI provider adapters and durable cloud persistence are intentionally separate modules and must be configured before production jobs can run.
