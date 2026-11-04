# Public Codespaces demonstration

Verified at **2026-11-04 22:25:48 UTC** (5 November in the owner's local timezone).
Deployed runtime source: `0c007009dd5edc8efe23774c6cc0285e9f8e4921`.

- [MirrorCheck landing](https://stunning-parakeet-x5pw4rxv7q7phv454-8090.app.github.dev/demo-guide.html)
- [Interactive prototype](https://stunning-parakeet-x5pw4rxv7q7phv454-8090.app.github.dev/)
- [Recorded English demo](https://stunning-parakeet-x5pw4rxv7q7phv454-8090.app.github.dev/demo-video.html)
- [Measured results](https://stunning-parakeet-x5pw4rxv7q7phv454-8090.app.github.dev/benchmark.html)

## Verified publicly

No GitHub authentication or access-token header was used for the HTTP checks.
The landing, feed, profile, review, benchmark and video-player routes returned
HTTP 200. The MP4 returned HTTP 206 for a byte-range request. A browser opened
the landing and initialized its own isolated prototype session.

`/healthz` returned HTTP 200 with `ready: true`: the web process, both ML models
and local workers were healthy. Both standalone ML endpoints returned HTTP 200.
An actual cloud screenshot inspection used PaddleOCR, imagededup and Presidio,
found at least four copied photo regions and masked two contact regions.
The test screenshots contain fictional profiles and reserved example contacts.

The source changes passed **166 backend tests** locally. All **38 frontend
tests** passed locally and in the first successful Codespaces image build.
The earlier full Linux CI evidence remains linked in
`submission/RELEASE_013_VERIFICATION.json`; it is a separate, older run, not
evidence that this cloud Meta request passed.

## Unresolved Meta access from Codespaces

The configured key matches the local key, but the cloud environment received
HTTP 404 with `model_not_found` for `muse-spark-1.3`, and `GET /v1/models`
returned an empty list. A small structured text request from the local machine
with that same key returned HTTP 200. The cause of this environment-dependent
provider response has not been established; no region or billing diagnosis
has been confirmed.

The live cloud report did **not** complete. No failed report or warning label
was saved, and no fallback was presented as a Meta result. Cloud confirmation,
appeal and overturn were therefore not re-verified after a successful Meta report.
The recorded video remains a separate demonstration of an earlier successful run.

The readiness endpoint now checks the real model catalog with a two-second
timeout and a 30-second cache, without generating a completion. It returns
`ready: false`, `meta_key_configured: true` and
`meta_model_access.state: not_listed` for this observed condition. The landing
correctly displays **Meta AI unavailable**. `/healthz` remains a check of the
application and local workers, separate from external model access.

## Hosting and privacy limits

Only port **8090** was made public. OCR/privacy workers remain on container
loopback. The Meta key is stored in the repository-scoped Codespaces secret
and the running server environment; it is not in source or these documents.
Existing local developer reports and evidence were not uploaded.

The two-core Codespace uses the verified remaining included allowance with a
**$0 stop budget**. Meta API usage is separate. This address works while the
Codespace runs; idle shutdown or quota exhaustion can take it offline. Before
an attended demo, start the Codespace, run `bash .devcontainer/start.sh`, check
health and model access, and verify that only 8090 is Public. Port visibility
may need to be reapplied after a restart. This deployment is not yet a fully
working live Meta demonstration or an always-on hosting service.
