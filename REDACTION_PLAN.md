# Automatic evidence redaction

Goal: locally detect contact identifiers using PaddleOCR + Presidio, permanently
cover the corresponding pixels before every Meta request, and show the exact
provider images in the reporting form and protected reviewer evidence.

Scope: opaque whole-line masks with padding, EXIF-aware coordinates, metadata
stripping, deterministic JPEG previews and SHA-256 audit, server enforcement even
without a browser inspection ticket, and fail-closed provider calls.

Non-goals: infer identity, change the Meta prompt/model, guarantee detection of all
PII or unreadable text, retroactively modify existing complaints, blur pixels or
rely on CSS overlays for privacy.

Acceptance: captured outgoing Meta JPEG bytes equal the preview and reviewer
evidence; email/phone regions are unreadable pixels; unmasked areas remain useful;
invalid/unavailable inspection prevents network calls and complaint persistence;
prior complaints remain unchanged; real browser demonstration proves the flow.

Plan: failing pixel/transport/persistence tests -> server implementation ->
redacted preview UI/tests -> relevant checks -> real Meta browser demonstration.

Completed 2026-11-03, version 0.8.0: fictional claim 2ee6228b used the real Meta
provider with 2 masked identifier regions. Browser preview bytes equal provider
JPEG hashes and stored reviewer bytes. A second real OCR/Presidio pass found zero
identifiers; all 6 photo matches remained. The new report is under_review; all
8 earlier complaints are unchanged. 122 backend and 18 frontend tests, the build,
formatting and secret checks passed. Evidence and before/after browser captures:
outputs/browser-redaction-20261103 and /redaction-walkthrough.html.
