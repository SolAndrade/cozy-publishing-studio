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
**Do not deploy the worker yet**. OpenAI image/vision adapters exist, but real provider
execution remains deliberately disabled unless `COZY_ENABLE_PAID_PROVIDERS=true` is
set in the private worker environment. Do not enable that flag without explicit cost
authorization. Render workers are separate services and need the same private database
URL plus durable private artifact storage. PostgreSQL jobs use atomic claims and claim
tokens; stale RUNNING jobs are blocked in production for explicit review rather than
automatically replayed.

## Current boundary

The API can persist projects and enqueue jobs in PostgreSQL. Provider adapters and
stale-job fencing are implemented, but end-to-end production generation remains
disabled until a durable private artifact store, an access boundary suitable for the
browser, and explicitly authorized provider execution are configured. KDP draft
integration is still outstanding. Final publication always requires a human.
