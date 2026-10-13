# Deployment

## Frontend

The public static dashboard is deployed to GitHub Pages. Do not put bearer tokens,
provider credentials, database URLs or unpublished assets in `config.js`.

## Render API + PostgreSQL (staging bootstrap)

`render.yaml` declares a web API and a private-network PostgreSQL database.
Render supplies `DATABASE_URL` using a database reference and generates
`COZY_API_TOKEN` privately. The API uses the same PostgreSQL database for
projects and queued jobs. The health endpoint `GET /health` is public;
`/api/*` requires the bearer token in production.

To provision, connect the GitHub repository in the Render dashboard and create
a Blueprint from `render.yaml`. Review resources and costs **before** approving
creation. A free PostgreSQL instance is temporary (Render currently expires
free databases after 30 days) and is NOT a durable commercial production plan.
Choose a paid persistent database with backups before storing real production
projects or book assets.

Do not paste the generated API token into this public repository, GitHub Pages
or chat. A static browser frontend cannot securely keep a shared bearer token.
Before enabling private operations from the dashboard, implement a proper
user login/session boundary or access-controlled private frontend.

## Worker

`python -m backend.workers.app` is the standalone worker command.
**Do not deploy the worker yet**: production deliberately fails closed until
real image and vision provider adapters are implemented and authorized.
Render workers are separate services and need the same private database URL.
PostgreSQL job claims use row locks to prevent simultaneous claims; crashed
RUNNING jobs still require lease/recovery handling before reliable production use.

## Current boundary

The API can persist projects and enqueue jobs in PostgreSQL, but end-to-end
production generation is not ready. Real provider adapters, crash recovery,
private artifact storage, authentication suitable for the browser, and KDP draft
integration are still outstanding. Final publication always requires a human.
