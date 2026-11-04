# Public Codespaces demonstration

Verified at **2026-11-04 23:13 UTC** (5 November in the owner's local timezone).
Deployed runtime source: `edd71bf85a77e34cea46129a28763fba65956166`.

- [MirrorCheck landing](https://congenial-garbanzo-4j5v4xwwx9r3jw9v-8090.app.github.dev/demo-guide.html)
- [Interactive prototype](https://congenial-garbanzo-4j5v4xwwx9r3jw9v-8090.app.github.dev/)
- [Recorded English demo](https://nurzhan-zhumabekov.github.io/META/)
- [Measured results](https://congenial-garbanzo-4j5v4xwwx9r3jw9v-8090.app.github.dev/benchmark.html)

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

## Live Meta access restored in US West

The first Codespace was in CentralIndia and returned an empty model catalog
and HTTP 404 `model_not_found`. A replacement explicitly created in US West
reports `WestUs2`. The same key, model and HTTP/1.1 client work there. No key
rotation, payment change or fallback was required. This observed difference
does not establish a regional restriction policy or diagnose Meta's service.
The console's Models page still showed no available models during inspection.

The new public API flow completed a real, uncached `muse-spark-1.3` analysis,
both ML signals, four copied photo regions and two contact masks. Processed
preview bytes exactly matched saved reviewer evidence. The claim remained
`under_review` until an explained moderator confirmation added the warning.
A scoped appeal and explicit overturn removed it. Private history recorded
the transition; unauthorized reports and evidence access were denied.
See [machine-readable cloud evidence](../submission/PUBLIC_CLOUD_VERIFICATION.json).
These are functional checks on fictional fixtures, not real-world accuracy.
The recorded video remains a separate demonstration of an earlier local run.

The readiness endpoint now checks the real model catalog with a two-second
timeout and a 30-second cache, without generating a completion. It returns
`ready: true`, `meta_key_configured: true` and
`meta_model_access.state: available` in the verified replacement. `/healthz` remains a check of the
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
may need to be reapplied after a restart. The independent GitHub Pages video
does not require a running Codespace. This is temporary attended hosting,
not an always-on hosting service.
