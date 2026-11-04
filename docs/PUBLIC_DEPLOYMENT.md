# Public demo deployment

The owner chose a free hosting path. No paid Render service is authorized or created. See `FREE_DEMO_HOSTING.md` for the prepared temporary Codespaces option; this Render blueprint remains an optional paid alternative.

The prepared deployment uses one Docker service with separate API, PaddleOCR/imagededup and Presidio Python environments. Only the web/API port is exposed; workers bind to loopback and require a private generated key. The supervisor drops root privileges before starting application processes. `GET /healthz` requires both bundled models, the local workers, public-demo signing configuration and a Meta key when Meta mode is selected. It never makes a paid model request.

## Before provisioning

`render.yaml` selects **2c-4g paid compute**, one instance, Frankfurt, and a 1 GB persistent disk. On 5 November 2026, the rendered official pricing table lists $85/month for 2c-4g and $0.25/GB/month for disks: $85.25/month for this configuration, plus Meta usage, any workspace subscription, bandwidth overages and applicable taxes. Review the current quote and intended workspace before applying it. No paid service has been provisioned by this change. The blueprint passes the current official Render JSON Schema. Automatic deploys are disabled; deploy a reviewed, passing commit deliberately.

Enter `META_API_KEY` only in Render's secret environment interface. The blueprint generates `DEMO_SESSION_SECRET`; it contains no real keys. Do not upload `.env`, local reports, raw research data or worker keys. Docker ignores those paths. Keep `PUBLIC_DEMO_ENABLED=true`, `COMPARER=meta`, `REQUIRE_META=true`. A missing Meta key fails startup, rather than falling back silently.

Each signed visitor session has a separate SQLite database and evidence folder. Demo moderator role-play applies only to that session. It never grants access to local/admin reports or another visitor's data. Appeal links in the public demo work only within that same browser session. There is no real Instagram ownership verification or production moderator identity system.

Sessions expire after two hours. Expired registered sandbox directories are removed after a ten-minute grace period, checked every five minutes by the Docker supervisor and on new admissions. Cookie clearing loses access sooner. Limits: 32 active sessions, 3 new sessions per IP/hour, 3 reports/session, 12 MB declared upload body, 2 simultaneous upload/inspection requests. Meta budgets default in the blueprint to 10/hour globally and 2/hour per submitted owner handle. Process-local limits reset on restart; these controls are for a bounded demo, not an internet-scale anti-abuse system.

## Build and verify

```sh
docker build --target test -t mirrorcheck:test .
docker build -t mirrorcheck:release .
docker run --rm -p 127.0.0.1:8090:8090 --env-file .env.public -v mirrorcheck-data:/var/data mirrorcheck:release
```

The test image runs the frontend, backend, real image-tool and privacy suites. GitHub Actions also runs the full sandbox/report/confirmation/appeal/overturn flow with real local workers and **zero Meta calls**. The Linux smoke flow also restarts the container and verifies persisted history/evidence under a 4 GB / 2 CPU limit. A separate real-Meta preflight and one live claim are required after deployment. Do not call a container build or an HTTP 200 alone a successful public launch.

At the HTTPS URL verify: `/healthz` ready; landing and app assets; Meta/OCR/privacy model status; no cross-visitor reports/evidence; processed preview bytes equal saved evidence; independent ML results; explained confirmation; private appeal; explained overturn; warning disappears; history survives service restart. Record the URL, deployed commit, real provider identity and time. Until these checks pass, public deployment remains pending.

## Persistence, backup and rollback

SQLite uses WAL and write transactions on `/var/data`. This is a single-instance demonstration; do not horizontally scale it. Render persistent disks prevent zero-downtime replacement. Back up a database through SQLite's backup API, not by copying a live database file without its WAL. Keep backups private. Local legacy `claims.json` is imported once, idempotently, from the same directory; its contents and evidence are retained. Old records without a reason remain visibly marked as legacy rather than receiving invented history.

Rollback the code/model image to the previous known-good commit after a database backup; never overwrite the persistent volume with developer outputs. The appeal/history fields are additive JSON payload fields. Older code may not understand them, so prefer rolling forward with a fix and retain backups. Restrict trusted proxy headers at the hosting ingress: the image's forwarded-header setting assumes it is reachable only through a managed proxy.
